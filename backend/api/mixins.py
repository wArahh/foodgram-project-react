from foodgram.models import Follow


class IsSubscriberMixin:
    def is_subscribed(self, subscribed_to):
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(
                subscriber=self.context['request'].user,
                subscribed_to=subscribed_to
            ).exists()
        return False
