from django import forms
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

from leaderboard.models import Match, Player

DUPLICATE_ERROR = 'Player has already been added with the same first and last name.'

MAX_SCORE = 30
MIN_WIN_SCORE = 11
INIT_RATING = 1450

class MatchForm(forms.ModelForm):
    """Form to submit a match result."""
    winner = forms.ModelChoiceField(queryset=Player.objects.order_by('first_name'),
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    loser = forms.ModelChoiceField(queryset=Player.objects.order_by('first_name'),
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    draw = forms.CheckboxInput(attrs={'class': 'form-check-input'}),

    def __init__(self, *args, **kwargs):
        """Initialize form with initial winning score of MIN_WIN_SCORE."""
        super().__init__(*args, **kwargs)
        self.min_score = MIN_WIN_SCORE
        self.fields['winning_score'].initial = self.min_score

    class Meta():
        model = Match
        fields = ['winner', 'winning_score', 'loser', 'losing_score', 'draw']
        widgets = {
            'winning_score': forms.NumberInput(attrs={'min': MIN_WIN_SCORE, 'max': MAX_SCORE, 'class': 'form-control'}),
            'losing_score': forms.NumberInput(attrs={'min': 0, 'max': MAX_SCORE, 'class': 'form-control'}),
        }

    def clean(self):
        """Validate winning and losing scores."""
        cleaned_data = super().clean()
        winning_score = cleaned_data.get('winning_score')
        losing_score = cleaned_data.get('losing_score')
        winner = cleaned_data.get('winner')
        loser = cleaned_data.get('loser')
        draw = cleaned_data.get('draw')

        if winner == loser:
            raise ValidationError('The winner and loser must be different players.')
        if winning_score < self.min_score:
            if winning_score != losing_score:
                raise ValidationError('Winning score must be ' + str(self.min_score) + ' or greater (except Draw).')
        if losing_score < 0:
            raise ValidationError('Losing score must be 0 or greater.')
        if winning_score == losing_score and draw == False:
            raise ValidationError(
                'If its a draw please tick the checkbox too! If not, please make sure the scores are different.'
            )
        if winning_score != losing_score and draw == True:
            raise ValidationError(
                'If its a draw please tick the checkbox too! If not, please make sure the scores are different.'
            )
        # if winning_score > self.min_score and winning_score - losing_score != 2:
        #     raise ValidationError(
        #         'Deuce game! Winner must win by exactly 2 points when above ' + self.min_score + '.'
        #     )


class PlayerForm(forms.ModelForm):
    """Form to add a new player."""
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    rating = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].initial = INIT_RATING

    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'rating']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': DUPLICATE_ERROR,
            }
        }
    
    def clean_first_name(self):
        """Capitalize first name."""
        return self.cleaned_data.get('first_name').capitalize()

    def clean_last_name(self):
        """Capitalize last name."""
        return self.cleaned_data.get('last_name').capitalize()
