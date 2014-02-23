#set encoding=utf-8

entities = dict(
    laquo = u'\u00AB',
    raquo = u'\u00BB')

REQUISITES = dict(
            name = u"ООО {laquo}Издательство ГРАНАТ{raquo}".format(
                **entities),
            INN = "7729707288",
            BIK = "044525986",
            KPP = "772901001",
            correspondentAccount = "30101810600000000986",
            beneficiaryAccount = "40702810000010066732",
            bankName = (u"Расчетный счет ОАО АКБ "
                u"{laquo}Пробизнесбанк{raquo} г. Москва".format(
                    **entities)),
            address=(u"121471, Москва г, Рябиновая ул, дом №44, пом.1, "
                u"тел. (499) 391-48-04"),
            manager = u"Рябцева Мария Александровна",
            accountant = u"Анурова Ольга Львовна"
            )
