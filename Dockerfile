FROM rstudio/plumber
MAINTAINER David Shumway <dshumw2@uic.edu>

# idbac prereqs
RUN apt-get update && apt-get install -y \
	zlib1g-dev \
	r-cran-ncdf4 \
	netcdf-bin

# install idbac
RUN R -e "install.packages('remotes')"
RUN R -e "remotes::install_github('chasemc/IDBacApp@*release')"

CMD ["/app/plumber.R"]
