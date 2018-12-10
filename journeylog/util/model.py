from separatedvaluesfield.models import SeparatedValuesField
from django.utils import six


class FixedSeparatedValuesField(SeparatedValuesField):
    @staticmethod
    def consider_value_as_empty_list(value):
        return not value or value == '' or value == ['']

    def to_python(self, value):
        if self.consider_value_as_empty_list(value):
            return None

        values = value
        if isinstance(value, six.string_types):
            values = value.split(self.token)

        return [self.cast(v) for v in values]

    def get_db_prep_value(self, value, *args, **kwargs):
        if self.consider_value_as_empty_list(value):
            return ''

        assert(isinstance(value, list) or isinstance(value, tuple))

        return self.token.join(['%s' % s for s in value])
