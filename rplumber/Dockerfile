FROM rstudio/plumber
RUN apt-get update && apt-get install -y \
        zlib1g-dev \
        r-cran-ncdf4 \
        netcdf-bin \
        netcat \
        r-base-core \
        libnetcdf-dev
RUN R -e "install.packages('remotes')"
#RUN R -e "remotes::install_github('chasemc/IDBacApp@*release')"
RUN R -e "remotes::install_github('chasemc/IDBacApp@prioritizer')"
RUN apt-get install -y libpq-dev # requirement for RPostgreSQL
RUN R -e "install.packages('RPostgreSQL')"
