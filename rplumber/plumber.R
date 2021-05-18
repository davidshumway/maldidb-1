#* Example query:
#* $ curl -H "Content-Type: application/json" --data '{"ids":[1,2,3]}'
#*   http://localhost:8000/sum

suppressPackageStartupMessages(library(IDBacApp))
require('RPostgreSQL')
library(curl)
library(jsonlite)

#* Echo
#*
#* @get /test
function() {
  return(
    list(name = 'Test')
  )
}

#* Return driver and connection
connect <- function() {
  # env variables
  POSTGRES_USER <- Sys.getenv('POSTGRES_USER')
  POSTGRES_PASSWORD <- Sys.getenv('POSTGRES_PASSWORD')
  POSTGRES_DB <- Sys.getenv('POSTGRES_DB')
  DATABASE_HOST <- Sys.getenv('DATABASE_HOST')
  DATABASE_PORT <- Sys.getenv('DATABASE_PORT')
  drv <- dbDriver('PostgreSQL')
  con <- dbConnect(
    drv, dbname = POSTGRES_DB,
    host = DATABASE_HOST, port = DATABASE_PORT,
    user = POSTGRES_USER, password = POSTGRES_PASSWORD
  )
  list('drv' = drv, 'con' = con)
}
disconnect <- function(driver, connection) {
  dbDisconnect(connection)
  dbUnloadDriver(driver)
}

# auxiliary print function
print.data.frame <- function (
  x, ..., maxchar=20, digits = NULL, quote = FALSE, right = TRUE,
  row.names = TRUE) 
{
  x <- as.data.frame(
    lapply(x, function(xx) {
      if (is.character(xx))
        paste0(substr(xx, 1, maxchar), '...')
      else if (is.list(xx))
        xx
      else xx
    })
  )
  base::print.data.frame(
    x, ..., digits=digits, quote=quote, right=right, 
    row.names=row.names
  )
}

#* Bin peaks: Get cosine scores for an unknown vs. set of db spectra
#*  -- ids must correlate to at least 1 row
#*     furthermore, stop if ids does not match db results??
#*  -- id refers to spectra in question, from SearchSpectra table
#* @param req Built-in
#* @param id List of IDs from SearchSpectra table
#* @param ids List of IDs from Spectra table
#* @post /binPeaks
function(req, id, ids) {
  if (class(ids) != 'integer') {
    stop('not an integer (ids)!') # stop throws 500
  }
  if (class(id) != 'integer') {
    stop('not an integer (id)!')
  }
  if (length(ids) < 1) {
    stop('less than one comparison id given!')
  }
  
  c <- connect()
  s <- paste(unlist(ids), collapse = ',')
  s <- paste0('SELECT peak_mass, peak_intensity, peak_snr
    FROM spectra_spectra
    WHERE id IN (', s, ')')
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 1) {
    disconnect(c$drv, c$con)
    stop('database returned less than one row (spectra)!')
  }
  s <- paste0('SELECT peak_mass, peak_intensity, peak_snr
    FROM spectra_searchspectra
    WHERE id = "', id, '"')
  q2 <- dbGetQuery(c$con, s)
  if (nrow(q2) != 1) {
    disconnect(c$drv, c$con)
    stop('database did not return exactly one row (searchspectra)!')
  }
  
  allSpectra = list()
  allPeaks = list()
  
  for(i in 1:nrow(q2)) { # unknown spectra
    row <- q2[i,]
    allPeaks <- append(allPeaks,
      MALDIquant::createMassPeaks(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]),
        snr = as.numeric(strsplit(row$peak_snr, ",")[[1]]))
    )
    allSpectra <- append(allSpectra,
      MALDIquant::createMassSpectrum(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]))
    )
  }
  for(i in 1:nrow(q)) {
    row <- q[i,]
    allPeaks <- append(allPeaks,
      MALDIquant::createMassPeaks(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]),
        snr = as.numeric(strsplit(row$peak_snr, ",")[[1]]))
    )
    allSpectra <- append(allSpectra,
      MALDIquant::createMassSpectrum(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]))
    )
  }
  
#~   print('len')
#~   print(length(allPeaks))columns
#~   print('dim')
#~   print(dim(allPeaks))
  
  binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
  featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)

  d <- stats::as.dist(coop::tcosine(featureMatrix))
  d <- as.matrix(d)
  d <- round(d, 3)
  d[lower.tri(d, diag = FALSE)] <- NA # Discard symmetric part of matrix
  d <- d[1,] # return just first row
  
  disconnect(c$drv, c$con)
  d
}

#* Cosine: Get cosine scores for a set of db spectra
#* Ids must correlate to at least 2 rows
#* Todo: library=, lab=, strain=, user=, ...
#* @param req Built-in
#* @param ids List of IDs from Spectra table
#* @post /cosine
function(req, ids) {
  #print('got ids')
  #print(ids)
  #print(class(ids))
  ids <- as.numeric(ids)
  if (length(ids) < 2) {
    stop('less than two comparison ids given!')
  }
  
  c <- connect()
  s <- paste(unlist(ids), collapse = ',')
  s <- paste0('SELECT peak_mass, peak_intensity, peak_snr, id
    FROM spectra_collapsedspectra
    WHERE id IN (', s, ')')
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 2) {
    disconnect(c$drv, c$con)
    stop('database returned less than two spectra!')
  }
  
  allSpectra = list()
  allPeaks = list()
  dbIds = list()
  
  for(i in 1:nrow(q)) {
    row <- q[i,]
    dbIds <- append(dbIds, row$id)
    allPeaks <- append(allPeaks,
      MALDIquant::createMassPeaks(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]),
        snr = as.numeric(strsplit(row$peak_snr, ",")[[1]]))
    )
    allSpectra <- append(allSpectra,
      MALDIquant::createMassSpectrum(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]))
    )
  }
  disconnect(c$drv, c$con)
  print(dbIds)
  binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
  featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
  d <- stats::as.dist(coop::tcosine(featureMatrix))
  d <- as.matrix(d)
  d <- round(d, 3)
  print(d)
  d[lower.tri(d, diag = FALSE)] <- NA # Discard symmetric part of matrix
  d <- d[1,] # return just first row
  return(d)
  
  
  t <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
  # non-collapsed spectra:
  #     t <- MALDIquant::filterPeaks(t, minFrequency = 70 / 100)
  #     t <- MALDIquant::mergeMassPeaks(t, method = 'mean')
#~   print('x')
#~   print(head(t))
#~   t <- list(t)
#~   print(lapply(t, MALDIquant::isEmpty))
  
  emptyProtein <- unlist(
    lapply(t, MALDIquant::isEmpty)
  )
  
  test <- lapply(t, function(x) x@mass)
#~   test <- lapply(t[!emptyProtein], function(x) x@mass)
  print(head(test,2))
  test <- lapply(t[!emptyProtein], function(x) x@intensity)
  print(head(test,2))
  proteinMatrix <- IDBacApp:::createFuzzyVector(
    massStart = 2000,
    massEnd = 20000,
    ppm = 1000,
    massList = lapply(t[!emptyProtein], function(x) x@mass),
    intensityList = lapply(t[!emptyProtein], function(x) x@intensity))
  print(head(proteinMatrix, 1))
  x <- idbac_dendrogram_creator(
    bootstraps = 0L,
    distanceMethod = 'cosine',
    clusteringMethod = 'average',
    proteinMatrix
  )
  print(x)
  return(x)
  
#~   featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
#~   d <- stats::as.dist(coop::tcosine(featureMatrix))
#~   d <- as.matrix(d)
#~   d <- round(d, 3)
#~   dfull <- d
#~   d[lower.tri(d, diag = FALSE)] <- NA # Discard symmetric part
#~   disconnect(c$drv, c$con)
#~   library(jsonlite)
#~   a <- list( # capture output helpful for serializing S4 class
#~     'ids' = ids,
#~     'allPeaks' = capture.output(allPeaks),
#~     'allSpectra' = capture.output(allSpectra),
#~     'binnedPeaks' = capture.output(binnedPeaks),
#~     'featureMatrix' = capture.output(featureMatrix),
#~     'cosineScores' = capture.output(dfull),
#~     #'cosineScoresUt' = capture.output(d),
#~     'cosineScoresUt' = d
#~   )
#~   jsonlite::toJSON(a)
}

# Helper function to retrive list of IDs from Django's DB
dbSpectra <- function(ids) {
  if (class(ids) != 'integer') {
#~     print(class(ids))
    stop('dbSpectra: not integer!') # stop throws 500
  }
  if (length(ids) < 1) {
    stop('less than one comparison id given!')
  }
  
  c <- connect()
  s <- paste(unlist(ids), collapse = ',')
  s <- paste0('SELECT peak_mass, peak_intensity, peak_snr
    FROM spectra_spectra
    WHERE id IN (', s, ')')
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 1) {
    disconnect(c$drv, c$con)
    stop('database returned less than one row (spectra)!')
  }
    
  allSpectra = list()
  allPeaks = list()
  
  for(i in 1:nrow(q)) {
    row <- q[i,]
    allPeaks <- append(allPeaks,
      MALDIquant::createMassPeaks(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]),
        snr = as.numeric(strsplit(row$peak_snr, ",")[[1]]))
    )
    allSpectra <- append(allSpectra,
      MALDIquant::createMassSpectrum(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]))
    )
  }
  
  list('peaks' = allPeaks, 'spectra' = allSpectra)
}

#* Collapse every strain in a given library
#* @param id Library id to collapse
#* @param owner User undertaking the process
#* @param taskId Reference to a Django user task
#* @get /collapseLibrary
collapseLibrary <- function(id, owner, taskId) {
#~   if (class(id) != 'integer') {
#~     stop('not an integer!')
#~   }
  c <- connect()
  s <- paste0('SELECT distinct(strain_id) as strain_id
    FROM spectra_spectra
    WHERE library_id = ', as.numeric(id))
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 1) {
    disconnect(c$drv, c$con)
    stop('no strain IDs in library!')
  }
  disconnect(c$drv, c$con)
  for(i in 1:nrow(q)) {
    row <- q[i,]
    print(paste0(
      'collapsing pr/sm for strain_id: ', as.character(row), '...'
    ))
    collapseStrainsInLibrary(id, row, 'PR', owner)
    collapseStrainsInLibrary(id, row, 'SM', owner)
  }
  
  #* Show task complete
#~   c <- connect()
#~   s <- paste0('INSERT INTO chat_usertask
#~     WHERE library_id = ', as.numeric(id))
#~   q <- dbGetQuery(c$con, s)
#~   disconnect(c$drv, c$con)
}
#* Collapse a single strain (sid) from a single library (lid)
#* e.g. http://localhost:7002/collapseLibraryStrains?lid=1&sid=1&type=protein
#* @param lid
#* @param sid
#* @param type: protein or sm
#* @param owner: User undertaking the process
#* @get /collapseStrainsInLibrary
collapseStrainsInLibrary <- function(lid, sid, type, owner) {
  lid <- as.numeric(lid)
  sid <- as.numeric(sid)
  owner <- as.numeric(owner)
  if (type == 'PR')
    sym <- '>'
  else {
    sym <- '<'
    type <- 'SM' # validate
  }
  c <- connect()
  s <- paste0('SELECT peak_mass, peak_intensity, peak_snr, id
    FROM spectra_spectra
    WHERE library_id = ', as.numeric(lid), ' AND strain_id = ',
    as.numeric(sid), ' AND max_mass ', sym, ' 6000'
  )
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 1) {
    disconnect(c$drv, c$con)
    return()
#~     stop('no spectra matching library and strain!')
  } else if (nrow(q) < 2) {
    disconnect(c$drv, c$con)
    return()
#~     stop('library + strain produce only one spectra!')
  }
  
  allPeaks = list()
  strainIds = c()
  
  for(i in 1:nrow(q)) {
    row <- q[i,]
    strainIds <- append(strainIds, row$id)
    allPeaks <- append(allPeaks,
      MALDIquant::createMassPeaks(
        mass = as.numeric(strsplit(row$peak_mass, ",")[[1]]),
        intensity = as.numeric(strsplit(row$peak_intensity, ",")[[1]]),
        snr = as.numeric(strsplit(row$peak_snr, ",")[[1]]))
    )
  }
  disconnect(c$drv, c$con)
  
  t <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
  
  # minFrequency: double, remove all peaks which occur in less than
  #  minFrequency*length(l) '>MassPeaks objects. It is a relative threshold.
  # minNumber: double, remove all peaks which occur in less than
  #  minNumber '>MassPeaks objects. It is an absolute threshold.
  # e.g. minNumber = 1
  
  t <- MALDIquant::filterPeaks(t, minFrequency = 70 / 100)
  t <- MALDIquant::mergeMassPeaks(t, method = 'mean')
  
  # save to Django's DB
  # --curl
  #  "Content-Type: application/json" 
  h <- new_handle()
  x <- paste0(
    '{',
      '"peak_mass":', mqSerial(MALDIquant::mass(t)), ',',
      '"peak_intensity":', mqSerial(MALDIquant::intensity(t)), ',',
      '"peak_snr":', mqSerial(MALDIquant::snr(t)), ',',
      '"max_mass":', as.character(round(max(MALDIquant::mass(t)))), ',',
      '"min_mass":', as.character(round(min(MALDIquant::mass(t)))), ',',
      '"strain_id":', as.character(sid), ',',
      '"library":', as.character(lid), ',',
      '"min_snr":0.25,',
      '"tolerance":0.002,',
      '"peak_percent_presence":0.7,',
      '"spectra_content":"', as.character(type), '",',
      '"created_by":"', owner, '",',
      '"collapsed_spectra":', toJSON(strainIds),
    '}'
  )
  handle_setheaders(h,
    'Content-Type' = 'application/json',
    'Cache-Control' = 'no-cache'
  )
  handle_setopt(h, copypostfields = x)
  req <- curl_fetch_memory('http://django:8000/spectra/cs/', handle = h)
  if (req$status_code >= 300) {
    stop('status code:', req$status_code)
  }
}
#* @param l: List to serialize
mqSerial <- function(l) {
  as.character(paste0('"', paste(l, collapse = ','), '"'))
}

#* Preprocess: Preprocess spectra file uploads
#* @param file File path to preprocess
#* @return File path of resulting sqlite file
#* @get /preprocess
preprocess <- function(file) {
#~   f <- file.path(paste0("/app/", file))
#~   mzML_con <- mzR::openMSfile(f, backend = "pwiz")
#~   scanNumber <- nrow(mzR::header(mzML_con))
#~   print('scanNumber:')
#~   print(scanNumber)
#~   ids <- c(1:1000)
  
  mzFilePaths <- list(file.path(paste0("/app/", file)))
  sIDs <- base::basename(tools::file_path_sans_ext(mzFilePaths))
  print('sIDs')
  print(sIDs)
  f <- sanitize(sub('uploads/sync/', '', file))
  print('f')
  print(f)
  IDBacApp:::idbac_create(
    fileName = f,
    filePath = './uploads/sync/')
  idbacPool <- IDBacApp:::idbac_connect(
    fileName = f,
    filePath = './uploads/sync/')[[1]]
  IDBacApp:::spectraProcessingFunction(
    rawDataFilePath = file.path(paste0("/app/", file)),
    sampleID = sIDs,
    pool = idbacPool, 
    acquisitionInfo = NULL,
  )
#~   IDBacApp:::db_from_mzml(
#~     mzFilePaths = mzFilePaths,
#~     sampleIds = sIDs,
#~     idbacPool = idbacPool,
#~     acquisitionInfo = NULL) #...)
  
  # add as django Spectra
  # connect the django Spectra to the django UserFile
  # perform a cosine similarity scoring
  
  # return location of the idbac sqlite file.  
  print('return f')
  print(f)
  return(f)
  
  spectra <- IDBacApp:::idbac_get_spectra( # createMassSpectrum
    idbacPool, sIDs, "protein", MALDIquant = TRUE
  )
  # Collapse a sample's MALDIquant peak objects into a single peak object
  # return a single trimmed and binned MALDIquant peak object
  # 9016 x 1 sparse Matrix of class "dgCMatrix".
  
  peaks <- IDBacApp:::idbac_get_peaks(
    idbacPool,
    sIDs,
    minFrequency = 0,
    minNumber = NA, 
    lowerMassCutoff = 2000,
    upperMassCutoff = 20000, 
    minSNR = 3,
    tolerance = 0.002,
    type = "protein",
    mergeReplicates = TRUE,
    method = "strict",
    verbose = FALSE
  )
  print(peaks)
  emptyProtein <- unlist(
    lapply(peaks, MALDIquant::isEmpty)
  )
  print(emptyProtein)
  a <- dbSpectra(ids)
  #peaks <- c(peaks, a['peaks'])
  #print(peaks)
  
  proteinMatrix <- IDBacApp:::createFuzzyVector(
    massStart = 2000,
    massEnd = 20000,
    ppm = 1000,
    massList = lapply(peaks[!emptyProtein], function(x) x@mass),
    intensityList = lapply(peaks[!emptyProtein], function(x) x@intensity))
  print(proteinMatrix)
  x <- idbac_dendrogram_creator(
    bootstraps = 0L,
    distanceMethod = 'cosine',
    clusteringMethod = 'average',
    proteinMatrix
  )
  print(x)
  
  pool::poolClose(idbacPool)
}
sanitize <- function(filename, replacement = "") {
  illegal <- "[/\\?<>\\:*|\":]"
  control <- "[[:cntrl:]]"
  reserved <- "^[.]+$"
  windows_reserved <- "^(con|prn|aux|nul|com[0-9]|lpt[0-9])([.].*)?$"
  windows_trailing <- "[. ]+$"
  
  filename <- gsub(illegal, replacement, filename)
  filename <- gsub(control, replacement, filename)
  filename <- gsub(reserved, replacement, filename)
  filename <- gsub(windows_reserved, replacement, filename, ignore.case = TRUE)
  filename <- gsub(windows_trailing, replacement, filename)
  filename <- gsub("\\.","_", filename)
  filename <- gsub(" ", "_", filename)
  
  while (grepl("__", filename)) {
    filename <- gsub("__","_", filename)
  }
  
  # TODO: this substr should really be unicode aware, so it doesn't chop a
  # multibyte code point in half.
  filename <- substr(filename, 1, 50)
  if (replacement == "") {
    return(filename)
  }
  sanitize(filename, "")
}

#* Preprocess: Preprocess spectra files
#* e.g.,   observeEvent(input$runMsconvert, { ...
#* @param file File path to preprocess
#* @get /preprocess
preprocess2 <- function(file) {
  smallRangeEnd <- 6000
  f <- file.path(paste0("/app/", file))
  mzML_con <- mzR::openMSfile(f, backend = "pwiz")
  scanNumber <- nrow(mzR::header(mzML_con))
  print('scanNumber:')
  print(scanNumber)
  
  # matrix
  spectraImport <- mzR::peaks(mzML_con)
  #print('spectraImport1')
  #print(class(spectraImport))
  #print(spectraImport)
  
  # mass spectrum
  spectraImport <- IDBacApp::spectrumMatrixToMALDIqaunt(spectraImport)
  #print('spectraImport2')
  #print(class(spectraImport))
  #print(spectraImport)
  
  # logical vector of maximum masses of mass vectors.
  # True = small mol, False = protein
  smallIndex <- unlist(lapply(spectraImport, function(x) max(x@mass)))
  smallIndex <- smallIndex < smallRangeEnd
  envSm <- FALSE
  envPr <- FALSE
  if (any(smallIndex)) {
   envSm <- IDBacApp::processXMLIndSpectra(
     spectraImport = spectraImport,
     smallOrProtein = "small",
     index = smallIndex)
  }
  if (any(!smallIndex)) {
   envPr <- IDBacApp::processXMLIndSpectra(
     spectraImport = spectraImport,
     smallOrProtein = "protein",
     index = !smallIndex)
    x <- collapseReplicates(
      IDBacApp::processProteinSpectra(spectraImport[!smallIndex])
    )
  }
  
  # write to db
  # UserFile = get$file
  # Spectra = get$spectra
#~   print('env')
#~   print(envSm)
#~   print(envPr)
#~   print(x)
  #return(list('x' = capture.output(x)))
  x
}

collapseReplicates <- function(temp) {
#~     checkedPool,
#~     sampleIDs,
#~     peakPercentPresence,
#~     lowerMassCutoff,
#~     upperMassCutoff, 
#~     minSNR, 
#~     tolerance = 0.002,
#~     protein
#~   validate(need(is.numeric(peakPercentPresence), "peakPercentPresence not numeric"))
#~   validate(need(is.numeric(lowerMassCutoff), "lowerMassCutoff not numeric"))
#~   validate(need(is.numeric(upperMassCutoff), "upperMassCutoff not numeric"))
#~   validate(need(is.numeric(minSNR), "minSNR not numeric"))
#~   validate(need(is.numeric(tolerance), "tolerance not numeric"))
#~   validate(need(is.logical(protein), "protein not logical"))
  #temp <- IDBacApp::getPeakData(checkedPool = checkedPool,
  #                              sampleIDs = sampleIDs,
  #                              protein = protein) 
  # getPeakData::
#~   temp <- lapply(temp,
#~    function(x){
#~      MALDIquant::createMassPeaks(
#~        mass = x$mass,
#~        intensity = x$intensity ,
#~        snr = as.numeric(x$snr))
#~    }
#~   )
  minSNR <- 3 # min SNR is 3 for protein data
  tolerance <- 0.002
  peakPercentPresence <- 70
  lowerMassCutoff <- 2000
  upperMassCutoff <- 20000
  
  req(length(temp) > 0)
  
  # Binning peaks lists belonging to a single sample so we can filter 
  # peaks outside the given threshold of presence 
  for (i in 1:length(temp)) {
   snr1 <-  which(MALDIquant::snr(temp[[i]]) >= minSNR)
   temp[[i]]@mass <- temp[[i]]@mass[snr1]
   temp[[i]]@snr <- temp[[i]]@snr[snr1]
   temp[[i]]@intensity <- temp[[i]]@intensity[snr1]
  }

  specNotZero <- sapply(temp, function(x) length(x@mass) > 0)

  # Only binPeaks if spectra(um) has peaks.
  # see: https://github.com/sgibb/MALDIquant/issues/61 for more info 
  # note: MALDIquant::binPeaks does work if there is only one spectrum
  if (any(specNotZero)) {
   temp <- temp[specNotZero]
   temp <- MALDIquant::binPeaks(temp,
                                tolerance = tolerance, 
                                method = c("strict"))
   temp <- MALDIquant::filterPeaks(temp,
                                   minFrequency = peakPercentPresence / 100)
   temp <- MALDIquant::mergeMassPeaks(temp,
                                      method = "mean")
   temp <- MALDIquant::trim(temp,
                            c(lowerMassCutoff,
                              upperMassCutoff))
  } else {
   temp <- MALDIquant::mergeMassPeaks(temp,
                                      method = "mean")
  }
  temp
}

# --------------------
# From rfn.py / Rpy2
# --------------------

# ~ R('''
# ~ createMassSpectrum__ <- function(mass, intensity) {
  # ~ MALDIquant::createMassSpectrum(mass, intensity)
# ~ }
# ~ createMassPeaks__ <- function(mass, intensity, snr) {
  # ~ MALDIquant::createMassPeaks(
    # ~ mass = mass, intensity = intensity, snr = as.numeric(snr)
  # ~ )
# ~ }
# ~ ''')

# ~ # bin
# ~ R('''
  # ~ showMem <- function() {
    # ~ print('x')
    # ~ for (itm in ls()) { 
      # ~ print(formatC(c(itm, object.size(get(itm))), 
          # ~ format="d", 
          # ~ big.mark=",", 
          # ~ width=30), 
          # ~ quote=F)
    # ~ }
  # ~ }
  # ~ binPeaks <- function(allPeaks, allSpectra) {
    # ~ showMem()
    # ~ # Only scores in first row are relevant, i.e., input spectra
    # ~ # Finally, order the row by score decreasing
    # ~ binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
    # ~ # ram issue here:
    # ~ featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    # ~ showMem()
    
    # ~ d <- stats::as.dist(coop::tcosine(featureMatrix))
    # ~ d <- as.matrix(d)
    # ~ d <- round(d, 3)
    
    # ~ # Reorder later
    # ~ #d <- d[,order(d[,1],decreasing = T)]
    
    # ~ # Discard symmetric part of matrix
    # ~ d[lower.tri(d, diag = FALSE)] <- NA
    # ~ print(d[2,])
    
    # ~ d <- d[1,] # first row
  # ~ }
  # ~ binPeaksInfo <- function(allPeaks, allSpectra) {
    # ~ #library(jsonlite)
    # ~ # bp: a list of MassPeaks objects
    # ~ binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
    # ~ featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    # ~ d <- stats::as.dist(coop::tcosine(featureMatrix))
    # ~ d <- as.matrix(d)
    # ~ d <- round(d, 3)
    # ~ ut <- d
    # ~ ut[lower.tri(ut, diag = FALSE)] <- NA
    # ~ n <- list(
      # ~ "binnedPeaks" = binnedPeaks,
      # ~ "featureMatrix" = featureMatrix,
      # ~ "cosineScores" = d,
      # ~ "cosineScoresUt" = ut
    # ~ )
    # ~ #toJSON(n, pretty = FALSE)
    # ~ #return()
  # ~ }
  
  # ~ # heatmap code
  # ~ binSpectraOLD <- function() {
    # ~ binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
    # ~ featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    
    
    # ~ # Utilizing: github.com/strejcem/MALDIvs16S/blob/master/R/MALDIbacteria.R
    
    # ~ # IDBac: stats::as.dist(1 - coop::tcosine(data))
    # ~ d <- stats::as.dist(coop::tcosine(featureMatrix))
    
    # ~ x <- as.matrix(d)
    # ~ x <- round(x, 2)
    # ~ #print('d')
    # ~ #print(d)
    
    # ~ #jpeg(file = "test.jpg", quality = 100, width = 2000, height = 2000)
    # ~ png(file = "test.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    # ~ heatmap(x, symm = FALSE, Colv = NA, Rowv = NA) #, col = palette, symm = TRUE)
    # ~ dev.off()
    
    # ~ # small section
    # ~ png(file = "test-sm.png", width = 1000, height = 1000, res = 300, pointsize = 6)
    # ~ heatmap(x[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA) #, col = palette, symm = TRUE)
    # ~ dev.off()
    
    # ~ library(gplots)
    # ~ png(file = "test2-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ gplots::heatmap.2(x[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA, cellnote = x[1:16,1:16], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test2-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ gplots::heatmap.2(x[1:32,1:32], symm = FALSE, Colv = NA, Rowv = NA, cellnote = x[1:32,1:32], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test3-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[lower.tri(x, diag = FALSE)] <- NA
    # ~ gplots::heatmap.2(y[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA, cellnote = y[1:16,1:16], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test3-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[lower.tri(x, diag = FALSE)] <- NA
    # ~ gplots::heatmap.2(y[1:32,1:32], symm = FALSE, Colv = NA, Rowv = NA, cellnote = y[1:32,1:32], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test3-full.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[lower.tri(x, diag = FALSE)] <- NA
    # ~ gplots::heatmap.2(y, symm = FALSE, Colv = NA, Rowv = NA, trace = "none")
    # ~ dev.off()
    
    
    # ~ png(file = "test4-sm.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[y == 0] <- 1
    # ~ gplots::heatmap.2(y[1:16,1:16], symm = FALSE, cellnote = y[1:16,1:16], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test4-med.png", width = 1200, height = 1200, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[y == 0] <- 1
    # ~ gplots::heatmap.2(y[1:32,1:32], symm = FALSE, cellnote = y[1:32,1:32], notecex = 0.5, trace = "none")
    # ~ dev.off()
    
    # ~ png(file = "test4-full.png", width = 3000, height = 3000, res = 300, pointsize = 6)
    # ~ y <- x
    # ~ y[y == 0] <- 1
    # ~ gplots::heatmap.2(y, symm = FALSE, trace = "none")
    # ~ dev.off()
    
  # ~ }
# ~ ''')
