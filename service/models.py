from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class Kafic(models.Model):
    kreirano = models.DateTimeField(auto_now_add=True)
    naziv = models.CharField(max_length=100)
    adresa = models.CharField(max_length=100)
    opstina = models.ForeignKey('Opstina', related_name='Opstina.naziv')
    vlasnik = models.ForeignKey('auth.User', related_name='kafici',)
    json_url = models.CharField(max_length=100, null=True)


    def __unicode__(self):
        return self.naziv

    def save(self, *args, **kwargs):
        super(Kafic, self).save(*args, **kwargs)

    class Meta:
        ordering = ('naziv',)


class Opstina(models.Model):
    opstina_id = models.IntegerField(max_length=10)
    naziv = models.CharField(max_length=100)

    def __unicode__(self):
        return self.naziv

    def save(self, *args, **kwargs):
        super(Opstina, self).save(*args, **kwargs)

    class Meta:
        ordering = ('naziv',)