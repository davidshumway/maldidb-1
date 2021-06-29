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
  
  class Meta:
    unique_together = (('name', 'txid'),)
