# idbac and plumber
#FROM rstudio/plumber AS build_part_0
#RUN apt-get update && apt-get install -y \
#        zlib1g-dev \
#        r-cran-ncdf4 \
#        netcdf-bin
#RUN R -e "install.packages('remotes')"
#RUN R -e "remotes::install_github('chasemc/IDBacApp@*release')"
#CMD ["/app/plumber.R"]

# nginx uwsgi
FROM python:3

RUN apt-get update && apt-get install -y \
        zlib1g-dev \
        r-cran-ncdf4 \
        netcdf-bin \
        netcat \
        r-base-core \
        libnetcdf-dev

RUN R -e "install.packages('remotes')"
RUN R -e "install.packages('BiocManager')"
RUN R -e "BiocManager::install('mzR')"
RUN R -e "remotes::install_github('chasemc/IDBacApp@*release')"

# copy previous build to here.
#COPY --from=build_part_0 /usr/bin/R /usr/bin/R
#RUN R -e "print('Running R from Dockerfile-0')"

ENV PYTHONBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

# Create an app user 
RUN useradd --user-group --create-home --no-log-init --shell /bin/bash app

ENV APP_HOME=/home/app/web

# Create the staticfiles directory. This avoids permission errors. 
RUN mkdir -p $APP_HOME/static

WORKDIR $APP_HOME

COPY requirements.txt $APP_HOME
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . $APP_HOME

RUN chown -R app:app $APP_HOME

USER app:app

ENTRYPOINT ["/home/app/web/entrypoint.sh"]
