from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .fields import ThumbnailImageField


def _gen_image_name(instance, _):
    """
    Returns the upload path (relative to settings.MEDIA_ROOT) for the specified Team's image.
    """

    # Must "return a Unix-style path (with forward slashes)"
    return 'team-images' + '/' + str(instance.user.id) + '.png'


class Team(models.Model):
    """
    Database representation of a team participating in the competition.
    This enhances the user model, where the team name, password, formal email address etc. are stored. It is
    particularly attuned to django.contrib.auth.models.User, but should work with other user models as well.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)

    net_number = models.PositiveSmallIntegerField(null=True, unique=True)
    informal_email = models.EmailField(_('Informal email address'))
    image = ThumbnailImageField(upload_to=_gen_image_name, blank=True)
    affiliation = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    # NOP teams don't get included in the scoring
    nop_team = models.BooleanField(default=False, db_index=True)

    class ActiveObjectsManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(user__is_active=True)

    class ActiveNotNopObjectsManager(ActiveObjectsManager):
        def get_queryset(self):
            return super().get_queryset().filter(nop_team=False)

    # The first Manager in a class is used as default
    objects = models.Manager()
    # QuerySet that only returns Teams whose associated user object is not marked as inactive
    active_objects = ActiveObjectsManager()
    # QuerySet that only returns active Teams that are not marked as NOP team
    active_not_nop_objects = ActiveNotNopObjectsManager()

    def __str__(self):
        # pylint: disable=no-member
        return self.user.username


class File(models.Model):
    """
    File assigned to a specific team.
    Can be used to provide configuration files to teams.
    """

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.TextField()
    data = models.BinaryField()
