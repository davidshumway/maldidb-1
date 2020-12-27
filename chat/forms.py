from django import forms

from .models import Comment, Spectra, Metadata, XML, Locale, Version, Library, PrivacyLevel

#from django.contrib.auth.models import User
#from django.contrib.auth import User
from django.contrib.auth import get_user_model
user = get_user_model()


class AddLibraryForm(forms.ModelForm):
	#title = forms.CharField(max_length=50)
	#library = forms.ModelMultipleChoiceField(
	#	queryset = Library.objects.all() # todo: add more description per entry
	#)
	#file = forms.FileField()
	
	class Meta:
		model = Library
		#fields = ('picture', 'text', 'peaks', 'intensities', 'md')
		exclude = ()
	
class LoadSqliteForm(forms.Form):
	library = forms.ModelMultipleChoiceField(
		queryset = Library.objects.all(), to_field_name="title"
	)
	user = forms.ModelMultipleChoiceField(
		queryset = user.objects.all(), to_field_name="username"
		 #User.objects.all() # todo: add more description per entry
	)
	file = forms.FileField()
	PUBLIC = 'PB'
	PRIVATE = 'PR'
	privacyChoices = [
		(PUBLIC, 'Public'),
		(PRIVATE, 'Private'),
	]
	privacy_level = forms.MultipleChoiceField(choices = privacyChoices)
	# ~ privacy_level = forms.ModelMultipleChoiceField(
		# ~ queryset = PrivacyLevel.objects.all(), to_field_name="username"
		 # ~ #User.objects.all() # todo: add more description per entry
	# ~ )
	
	
class SpectraForm(forms.ModelForm):
	""" Form for handling addition of posts """
	
	#md = forms.ModelMultipleChoiceField(
	#	queryset = Metadata.objects.all() # todo: add more description per entry
	#)
	
	# ~ library = forms.ModelMultipleChoiceField(
		# ~ queryset = Library.objects.all()
	# ~ )
	# ~ user = forms.ModelMultipleChoiceField(
		# ~ queryset = user.objects.all() #User.objects.all() # todo: add more description per entry
	# ~ )
	
	#def save(self, commit=True):
		# ~ instance = super().save(commit=False)
		# ~ lib = self.cleaned_data['library']
		# ~ instance.library = lib[0]
		# ~ usr = self.cleaned_data['user']
		# ~ instance.user = usr[0]
		# ~ instance.save(commit)
		# ~ return instance
		
	class Meta:
		model = Spectra
		#fields = ('peaks', 'intensities')
		exclude = ()
		widgets = {
			'text': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': 'General description.'}
			),
			'peaks': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': 'A comma-separated list, e.g., "167.06,179.07,193.07".'}
			),
			'intensities': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': 'A comma-separated list, e.g., "0.4,0.2,0.6".'}
			),
		}

class XmlForm(forms.ModelForm):
	class Meta:
		model = XML
		fields = ('xml_hash','xml','manufacturer','model','ionization','analyzer','detector','instrument_metafile')
		# ~ widgets = {
			# ~ 'cKingdom': forms.Textarea(
				# ~ attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			# ~ ),
			# ~ 'cPhylum': forms.Textarea(
				# ~ attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			# ~ ),
			# ~ 'cClass': forms.Textarea(
				# ~ attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			# ~ ),
			# ~ 'cOrder': forms.Textarea(
				# ~ attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			# ~ ),
			# ~ 'cGenus': forms.Textarea(
				# ~ attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			# ~ ),
			# ~ 'cSpecies': forms.Textarea(
				# ~ attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			# ~ ),
		# ~ }
		
class MetadataForm(forms.ModelForm):
	""" Form for handling addition of metadata """
	                          
	class Meta:
		model = Metadata
		#fields = ('cKingdom','cPhylum','cClass','cOrder','cGenus','cSpecies')
		exclude = ()
		widgets = {
			'cKingdom': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			),
			'cPhylum': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			),
			'cClass': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			),
			'cOrder': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			),
			'cGenus': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			),
			'cSpecies': forms.Textarea(
				attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
			),
		}

class LocaleForm(forms.ModelForm):
	class Meta:
		model = Locale
		exclude = ()

class VersionForm(forms.ModelForm):
	class Meta:
		model = Version
		exclude = ()
		
class CommentForm(forms.Form):
	""" Form for adding comments"""

	text = forms.CharField(
		label="Comment",
		widget=forms.Textarea(attrs={'rows': 2})
	)

	def save(self, spectra, user):
		""" custom save method to create comment """

		comment = Comment.objects.create(text=self.cleaned_data.get('text', None), post=spectra, user=user)
