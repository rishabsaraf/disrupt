from account.models import Account
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    """
    The model class for categories of questions.
    """
    name = models.CharField(max_length=20, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        This function returns the readable display string
        :return: the category name
        """
        return self.name


class AbstractQuestion(models.Model):
    """
    The model class for all questions. All the question models will extend this class.
    """
    # Main fields
    title = models.CharField(max_length=50, blank=False)
    description = models.TextField(blank=True)

    # This field will be used fo filtering
    categories = models.ManyToManyField(Category, blank=True)

    # Fields for auditing.
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # This field will be used to handle the deletion of questions.
    # No question will ever be deleted, only the visibility will be controlled.
    # A question with false visibility will be considered as deleted.
    visibility = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        """
        This function returns the readable display string.
        :return: the title of the question suffixed with the id.
        """
        return self.title + ': ' + str(self.id)

    def delete(self):
        """
        This function deletes the question. The question is not deleted actually, but only the visibility is changed.
        """
        self.visibility = False
        self.save()


class Poll(AbstractQuestion):
    """
    The model class for polls. It extends the AbstractQuestion class. All the polls/objective questions will be of this
    type.
    """
    pass


class PollOption(models.Model):
    """
    The option for a question of Poll type.
    """
    question = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=50)
    votes = models.PositiveIntegerField(default=0)

    class Meta:
        # Each poll question should have unique PollOptions.
        unique_together = ('question', 'choice_text',)

    def __str__(self):
        """
        This function returns the readable display string for PollOption object.
        :return: the choice_text + the question's display text.
        """
        return self.choice_text + ' ' + str(self.question)


class Vote(models.Model):
    voter = models.ForeignKey(Account, on_delete=models.CASCADE)
    question = models.ForeignKey(Poll, on_delete=models.CASCADE)
    option = models.ForeignKey(PollOption)

    class Meta:
        unique_together = ('question', 'voter',)

    def __str__(self):
        return str(self.voter) + ': ' + str(self.question)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.option not in self.question.polloption_set.all():
            raise ValidationError(_('This option is not present in the question\'s option set'), code='invalid')

        option = self.option
        option.votes += 1
        option.save()
        super(Vote, self).save(force_insert=force_insert, force_update=force_update, using=using,
                               update_fields=update_fields)

    def delete(self, using=None, keep_parents=False):
        pass
