import json
from .models import Spectra

'''
todo:
-- If the list passed to MQ:binPeaks is too large, RAM use becomes
  too high / exhausted. In this case, we can work around by breaking
  the list into smaller manageable lists and performing binPeaks
  on these smaller lists. On each round of binPeaks, remove the low-
  scoring matches. If, on the next round, the list is still too large,
  do another round of smaller list binning. Realistically, this should
  never go past a few rounds.
-- allPeaks, allSpectra, and binnedPeaks all are, e.g., list=(...), len=24424
-- show a plot of memory size and number of spectra being compared
'''


class SpectraScores():
  
  def __init__(self, form = None):
    self.all_peaks = []
    self.all_spectra = []
    self.form = form
    self.ids = []
    if form != None:
      self.process_form()
  
  # ~ def bin_peaks(self):
    # ~ return R['binPeaks'](self.all_peaks, self.all_spectra)
    
  # ~ def append_spectra(self, mass, intensity, snr):
    # ~ m = robjects.FloatVector(json.loads('[' + mass + ']'))
    # ~ i = robjects.FloatVector(json.loads('[' + intensity + ']'))
    # ~ s = robjects.FloatVector(json.loads('[' + snr + ']'))
    # ~ self.all_peaks.append(
      # ~ R['createMassPeaks__'](m, i, s)
    # ~ )
    # ~ self.all_spectra.append(
      # ~ R['createMassSpectrum__'](m, i)
    # ~ )
  
  def info(self):
    '''
    Use with process_form to output binPeaks data for inspection.
    -- .post to plumber not working??
    -- binPeaksInfo contains:
        list(
          'binnedPeaks' = binnedPeaks,
          'featureMatrix' = featureMatrix,
          'cosineScores' = d
        )
    '''
    # urllib request does not work: requests "localhost" not "plumber" ??
    #from urllib import parse
    data = {'ids': self.ids}
    import requests
    r = requests.post('http://plumber:8000/cosine', data = data)
    a = json.loads(json.loads(r.text)[0])
    #print(a)
    a['ids'] = json.dumps(a['ids'], indent = 2).replace('"','')
    a['allPeaks'] = json.dumps(a['allPeaks'], indent = 2).replace('"','')
    a['allSpectra'] = json.dumps(a['allSpectra'], indent = 2).replace('"','')
    a['binnedPeaks'] = json.dumps(a['binnedPeaks'], indent = 2).replace('"','')
    a['featureMatrix'] = json.dumps(a['featureMatrix'], indent = 2).replace('"','')
    a['cosineScores'] = json.dumps(a['cosineScores'], indent = 2).replace('"','')
    a['cosineScoresUt'] = json.dumps(a['cosineScoresUt'], indent = 2).replace('"','')
    return a
    
  def process_form(self):
    n = Spectra.objects.all()
    n = n.filter(max_mass__gt = 6000)
    # optionals
    slib = self.form.cleaned_data['library'];
    slab = self.form.cleaned_data['lab_name'];
    ssid = self.form.cleaned_data['strain_id'];
    # ~ sxml = form.cleaned_data['xml_hashXX'];
    # ~ scrb = form.cleaned_data['created_byXX'];
    #print(f'fcd: {form.cleaned_data}' ) # 
    if slib.exists():
      n = n.filter(library__in = slib)
    if slab.exists():
      n = n.filter(lab_name__in = slab)
    if ssid.exists():
      n = n.filter(strain_id__in = ssid)
    # ~ if sxml.exists():
      # ~ n = n.filter(xml_hash__in = sxml)
    # ~ if scrb.exists():
      # ~ n = n.filter(created_by__in = scrb)
    # ~ n = n.order_by('xml_hash')
    self.ids = []
    for spectra in n:
      self.ids.append(spectra.id)
      # ~ self.append_spectra(
        # ~ spectra.peak_mass, spectra.peak_intensity, spectra.peak_snr
      # ~ )
    ## bin
    ## return self.bin_peaks()
      

