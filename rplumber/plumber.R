#* Example query:
#* $ curl -H "Content-Type: application/json" --data '{"ids":[1,2,3]}'
#*   http://localhost:8000/sum

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
  require('RPostgreSQL')
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
        xx #paste0(substr(xx, 1, maxchar), '...')
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
  s <- paste0('SELECT peak_mass,peak_intensity,peak_snr
    FROM chat_spectra
    WHERE id IN (', s, ')')
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 1) {
    disconnect(c$drv, c$con)
    stop('database returned less than one row (spectra)!')
  }
  s <- paste0('SELECT peak_mass,peak_intensity,peak_snr
    FROM chat_searchspectra
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
#~   print(length(allPeaks))
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
#*  -- ids must correlate to at least 2 rows
#* @param req Built-in
#* @param ids List of IDs from Spectra table
#* @post /cosine
function(req, ids) {
  print('got ids')
  print(ids)
  if (class(ids) != 'integer') {
    stop('not an integer (ids)!') # stop throws 500
  }
  if (length(ids) < 2) {
    stop('less than two comparison ids given!')
  }
  
  c <- connect()
  s <- paste(unlist(ids), collapse = ',')
  s <- paste0('SELECT peak_mass,peak_intensity,peak_snr
    FROM chat_spectra
    WHERE id IN (', s, ')')
  q <- dbGetQuery(c$con, s)
  if (nrow(q) < 2) {
    disconnect(c$drv, c$con)
    stop('database returned less than two rows (spectra)!')
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
  
  print('made mq')
  
  binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance = 0.002)
  featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
  
  print('ran mq')
  
#~   stop('d')
  d <- stats::as.dist(coop::tcosine(featureMatrix))
  d <- as.matrix(d)
  d <- round(d, 3)
  dfull <- d
  d[lower.tri(d, diag = FALSE)] <- NA # Discard symmetric part
#~   stop('d')
  disconnect(c$drv, c$con)
  
  print('returning')
  
  library(jsonlite)
  a <- list(
    'ids' = ids,
    'allPeaks' = allPeaks,
    'allSpectra' = allSpectra,
    'binnedPeaks' = binnedPeaks,
    'featureMatrix' = featureMatrix,
    'cosineScores' = dfull,
    'cosineScoresUt' = d
  )
#### jsonlite::toJSON(a) # simply returning the list or toJSON of list 
                         # =exception: "No method for S4 class:MassPeaks"
  jsonlite::serializeJSON(a)
  
#~   stop('d')
}
