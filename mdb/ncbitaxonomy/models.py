from django.db import models

# Create your models here.
class TxNode(models.Model):
  name = models.TextField(blank=False, null=False)
  txid = models.IntegerField(blank=False, null=False)
  # S: scientific name
  # T: type material
  nodetype = models.CharField(
    max_length = 1,
    choices = [
      ('s', 'scientific name'),
      ('t', 'type material'),
      ('y', 'synonym'),
      # ~ ('z', 'z'), # this is a type for entries created manually
        # e.g., for "NRRL B-2249 [[Streptomyces griseus subsp. alpha]]"
        # entering a "synonym" of "NRRL B-2249"
    ],
    default = 's',
  )
  
  # txtype and parent are from second file
  txtype = models.TextField(blank=True, null=True)
  parentid = models.IntegerField(blank=False, null=False)
  
  # ~ parent = models.ForeignKey(
    # ~ 'TxNode',
    # ~ on_delete = models.CASCADE,
    # ~ null=True, blank=True)
  # ~ # all parents as json field {p1:, p1-rank:, ..., pn:, pn-rank:}
  # ~ parents = models.TextField(blank=False, null=False)
  
  cKingdom = models.CharField(max_length = 255, blank = True)
  cPhylum = models.CharField(max_length = 255, blank = True)
  cClass = models.CharField(max_length = 255, blank = True)
  cOrder = models.CharField(max_length = 255, blank = True)
  cFamily = models.CharField(max_length = 255, blank = True)
  cGenus = models.CharField(max_length = 255, blank = True)
  cSpecies = models.CharField(max_length = 255, blank = True)
  cSubspecies = models.CharField(max_length = 255, blank = True)
  
  class Meta:
    unique_together = (('name', 'txid'),)
    indexes = [ # index the name to speed up search
      models.Index(fields = ['name'])
    ]
