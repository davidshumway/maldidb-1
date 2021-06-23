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
  
  # txtype and parent are from second file, added on second pass
  txtype = models.TextField(blank=True, null=True)
  parent = models.ForeignKey(
    'TxNode',
    on_delete = models.CASCADE,
    null=True, blank=True)
  
  class Meta:
    unique_together = (('name', 'txid'),)
