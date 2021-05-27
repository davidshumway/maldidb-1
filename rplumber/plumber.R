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

#* Cosine: Get cosine scores for a set of db spectra
#* Ids must correlate to at least 2 rows
#*     https://github.com/strejcem/MALDIvs16S/../R/MALDIbacteria.Rsimilarity
#*     coop::cosine(t(featureMatrix))
#* Todo: library=, lab=, strain=, user=, ...
#* Bug: database result is reordered on id acending
#* @param req Built-in
#* @param ids List of IDs from Spectra table
#* @post /cosine
function(req, ids) {
  #print('got ids')
  print(ids)
  #print(class(ids))
  ids <- as.numeric(ids)
  if (length(ids) < 2) {#----
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
    #print(row$)
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
  # (manual inspection)
  print(toString(featureMatrix[0,]))
  #print(toString(featureMatrix[1,]))
  #print(toString(featureMatrix[2,]))
  print(coop::cosine(featureMatrix[1,], featureMatrix[2,]))
  d <- coop::cosine(t(featureMatrix))
  d <- round(d, 3)
  return(d[1,])
  
  emptyProtein <- unlist(
    lapply(allPeaks, MALDIquant::isEmpty)
  )
  
  # Sparse matrix to hold the peak probability data
  # Columns are samples, rows are m/z/intensity probabilities 
  # transform back to actual m/z can be accessed via rownames()

  proteinMatrix <- IDBacApp:::createFuzzyVector(
    massStart = 1600,
    massEnd = 20000,
    ppm = 1000,
    massList = lapply(allPeaks[!emptyProtein], function(x) x@mass),
    intensityList = lapply(allPeaks[!emptyProtein], function(x) x@intensity))
    
#~   x <- IDBacApp:::idbac_dendrogram_creator(
#~     bootstraps = 0L,
#~     distanceMethod = 'cosine',
#~     clusteringMethod = 'average',
#~     proteinMatrix
#~   )
  
  d <- as.dist(coop::cosine(proteinMatrix)) # 1 - coop::cosine(proteinMatrix)
  d <- round(d, 3)
  print(head(d, 1))
  
  
  d <- as.matrix(d)
  d <- round(d, 3)
  #d[lower.tri(d, diag = FALSE)] <- NA # Discard symmetric part of matrix
#~   print(head(d, 2))
  d <- d[1,]
  return(d) # returns first row
  
  ## not used
  # visualizing the sparse matrix
  
  # 200k rows
  ordering <- sort(d, decreasing = F, index.return = T)
  ordering <- ordering$ix
  print(ordering)
  pmReorder <- proteinMatrix[, ordering]
  
  png(file = 'scatterplot.png',  width = 10, height = 10, units = 'in', res = 600)
  image(
    t(as.matrix(pmReorder)[1:10000,]),
    axes = FALSE,
    col = colorRampPalette(c("white", "darkorange", "black"))(30),
    breaks = c(seq(0, 3, length.out = 30), 1), #, 100)
    main = "Reduced matrix",
    useRaster = TRUE
  )
  dev.off()
  
  # times 1 when first column is not 0, otherwise 0
  x <- proteinMatrix * ceiling(proteinMatrix[, 1])
  
  # times first column
#~   x <- proteinMatrix * proteinMatrix[, 1]

  x <- x[, ordering]
  png(file = 'scatterplot2.png',  width = 10, height = 10, units = 'in', res = 600)
  image(
    t(as.matrix(x)[1:10000,]),
    axes = FALSE,
    col = colorRampPalette(c("white", "darkorange", "black"))(30),
    breaks = c(seq(0, 3, length.out = 30), 1), #, 100)
    main = "Reduced matrix",
    useRaster = TRUE
  )
  dev.off()
  
  redim_matrix <- function(
    mat,
    target_height = 100,
    target_width = 100,
    summary_func = function(x) max(x, na.rm = TRUE),
    output_type = 0.0, #vapply style
    n_core = 1 # parallel processing
    ) {

    if(target_height > nrow(mat) | target_width > ncol(mat)) {
      stop("Input matrix must be bigger than target width and height.")
    }

    seq_height <- round(seq(1, nrow(mat), length.out = target_height + 1))
    seq_width  <- round(seq(1, ncol(mat), length.out = target_width  + 1))

    # complicated way to write a double for loop
    do.call(rbind, parallel::mclapply(seq_len(target_height), function(i) { # i is row
      vapply(seq_len(target_width), function(j) { # j is column
        summary_func(
          mat[
            seq(seq_height[i], seq_height[i + 1]),
            seq(seq_width[j] , seq_width[j + 1] )
            ]
        )
      }, output_type)
    }, mc.cores = n_core))
  }
  
#~   genmatred <- redim_matrix(as.matrix(pmReorder), target_height = 600, target_width = 50) 
  g <- redim_matrix(as.matrix(x), target_height = 1000, target_width = ncol(x)) 
  png(file = 'scatterplot3.png')
  image(
    t(g),
    axes = F,
    col = colorRampPalette(c("white", "darkorange", "black"))(30),
    breaks = c(seq(0, 3, length.out = 30), 1), #, 100)
    main = "Reduced matrix",
    useRaster = T
  )
  dev.off()
  
#~   g <- redim_matrix(as.matrix(x), target_height = 1000, target_width = ncol(x)) 
#~   png(file = 'scatterplot4.png')
#~   image(
#~     t(g),
#~     axes = F,
#~     col = colorRampPalette(c("white", "darkorange", "black"))(30),
#~     breaks = c(seq(0, 3, length.out = 30), 1), #, 100)
#~     main = "Reduced matrix",
#~     useRaster = TRUE
#~   )
#~   dev.off()
  
#~   g <- redim_matrix(as.matrix(x), target_height = 1000, target_width = ncol(x)) 
#~   png(file = 'scatterplot5.png')
#~   Heatmap(
#~     g[nrow(g):1, ],
#~     col = circlize::colorRamp2(c(0, 1.5, 3), c("white", "darkorange", "black")),
#~     cluster_rows = FALSE, cluster_columns = FALSE,
#~     show_heatmap_legend = FALSE,
#~     use_raster = TRUE,
#~     raster_resize = TRUE, raster_device = "png",
#~     column_title = "With rasterisation"
#~   )
#~   dev.off()

  return(d)
  

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
collapseLibrary <- function(id, owner = F) {
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
}
#* Collapse a single strain (sid) from a single library (lid)
#* e.g. http://localhost:7002/collapseLibraryStrains?lid=1&sid=1&type=protein
#* @param lid
#* @param sid
#* @param type: protein or sm
#* @param owner: User undertaking the process, or None for anonymous
#* @get /collapseStrainsInLibrary
collapseStrainsInLibrary <- function(lid, sid, type, owner) {
  lid <- as.numeric(lid)
  sid <- as.numeric(sid)
  if (owner == F) {
    print('owner is anon.')
    owner <- ''
  } else {
    print('owner is not anon.')
    owner <- paste0('"created_by":"', as.numeric(owner), '",')
  }
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
    # no spectra matching library and strain
    disconnect(c$drv, c$con)
    return()
  } else if (nrow(q) < 2) {
    # library + strain produce only one spectra
    # allow ?
    #disconnect(c$drv, c$con)
    #return()
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
      owner,
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
  # test
  #dir <- system.file('./', package = 'MALDIquantForeign')
  #s <- import(file.path(dir, 'brukerflex'), verbose = F)
#~   mz <- mzR::openMSfile(f, backend = "pwiz")
#~   print(mzR::header(mz))
#~   fileName(mz)
#~   instrumentInfo(mz)
#~   runInfo(mz)
#~   close(mz)
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
