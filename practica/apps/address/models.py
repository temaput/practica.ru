from oscar.apps.address.abstract_models import (
    AbstractUserAddress, AbstractCountry)


class UserAddress(AbstractUserAddress):
    def active_address_fields(self, include_salutation=True):
        """
        Return the non-empty components of the address, but merging the
        title, first_name and last_name into a single line.
        """
        fields = [self.line4, self.line1, ', '.join((self.line2, self.line3))]
        if self.postcode != '000000':
            fields.insert(0, self.postcode)
        if include_salutation:
            fields = [self.salutation] + fields
        fields = [f.strip() for f in fields if f]
        return fields


class Country(AbstractCountry):
    pass
