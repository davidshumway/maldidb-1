FROM rstudio/plumber
RUN apt-get update && apt-get install -y \
        zlib1g-dev \
        r-cran-ncdf4 \
        netcdf-bin \
        netcat \
        r-base-core \
        libnetcdf-dev
RUN R -e "install.packages('remotes')"
RUN R -e "remotes::install_github('chasemc/IDBacApp@*release')"
RUN apt-get install -y libpq-dev # requirement for RPostgreSQL
RUN R -e "install.packages('RPostgreSQL')"

#RUN useradd --user-group --create-home --no-log-init --shell /bin/bash app
#ENV APP_HOME=/app
#RUN mkdir -p $APP_HOME/uploads
#WORKDIR $APP_HOME
#RUN chown -R app:app $APP_HOME
#USER app:app
#RUN addgroup --gid 1000 mgroup
#RUN adduser --disabled-password --gecos "" --force-badname --ingroup 1000 muser 
#USER muser
#USER 1000:1000
#WORKDIR /app #/plumber
#CMD ["/app/plumber.R"]
