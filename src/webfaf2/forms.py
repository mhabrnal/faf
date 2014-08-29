import datetime
from wtforms import Form, validators, SelectMultipleField, TextField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField, QuerySelectField
from pyfaf.storage import OpSysRelease, OpSysComponent
from pyfaf.storage.opsys import AssociatePeople, Arch
from pyfaf.storage.bugzilla import BUG_STATES
from pyfaf.problemtypes import problemtypes
from webfaf2 import db
from sqlalchemy import asc


class DaterangeField(TextField):
    date_format = "%Y-%m-%d"
    separator = ":"

    def __init__(self, label=None, validators=None,
                 default_days=14,
                 **kwargs):
        self.default_days = default_days
        if default_days:
            today = datetime.date.today()
            kwargs["default"] = lambda: (today - datetime.timedelta(days=self.default_days), today)
        super(DaterangeField, self).__init__(label, validators, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            s = valuelist[0].split(self.separator)
            if len(s) == 2:
                self.data = (datetime.datetime.strptime(s[0], self.date_format).date(), datetime.datetime.strptime(s[1], self.date_format).date())
                return
        if self.default_days:
            today = datetime.date.today()
            self.data = (today - datetime.timedelta(days=self. default_days), today)
        else:
            self.data = None

    def _value(self):
        if self.data:
            return self.separator.join([d.strftime(self.date_format) for d in self.data[:2]])
        else:
            return ""


class ProblemFilterForm(Form):
    opsysreleases = QuerySelectMultipleField("Releases", query_factory=lambda: db.session.query(OpSysRelease).all(), get_pk=lambda a: a.id, get_label=lambda a: str(a))
    components = QuerySelectMultipleField("Components", query_factory=lambda: db.session.query(OpSysComponent).order_by(asc(OpSysComponent.name)).all(), get_pk=lambda a: a.id, get_label=lambda a: str(a))
    daterange = DaterangeField("Date range", default_days=14)
    associate = QuerySelectField("Associate", allow_blank=True, blank_text="Not selected", query_factory=lambda: db.session.query(AssociatePeople).order_by(asc(AssociatePeople.name)).all(), get_pk=lambda a: a.id, get_label=lambda a: a.name)
    arch = QuerySelectMultipleField("Arch", query_factory=lambda: db.session.query(Arch).all(), get_pk=lambda a: a.id, get_label=lambda a: str(a))
    # state = SelectMultipleField("State", choices=[(s, s) for s in BUG_STATES])


class ReportFilterForm(Form):
    opsysreleases = QuerySelectMultipleField("Releases", query_factory=lambda: db.session.query(OpSysRelease).all(), get_pk=lambda a: a.id, get_label=lambda a: str(a))
    components = QuerySelectMultipleField("Components", query_factory=lambda: db.session.query(OpSysComponent).order_by(asc(OpSysComponent.name)).all(), get_pk=lambda a: a.id, get_label=lambda a: str(a))
    first_occurrence_daterange = DaterangeField("Fist occurrence", validators=[validators.Optional()], default_days=None)
    last_occurrence_daterange = DaterangeField("Last occurrence", validators=[validators.Optional()], default_days=None)
    associate = QuerySelectField("Associate", allow_blank=True, blank_text="Not selected", query_factory=lambda: db.session.query(AssociatePeople).order_by(asc(AssociatePeople.name)).all(), get_pk=lambda a: a.id, get_label=lambda a: a.name)
    arch = QuerySelectMultipleField("Arch", query_factory=lambda: db.session.query(Arch).all(), get_pk=lambda a: a.id, get_label=lambda a: str(a))
    type = SelectMultipleField("Type", choices=[(a, a) for a in problemtypes.keys()])
    order_by = SelectField("Order by", choices=[
        ("last_occurrence", "Last occurrence"),
        ("first_occurrence", "First occurrence"),
        ("count", "Count")],
        default="last_occurrence")


class BacktraceDiffForm(Form):
    lhs = SelectField("LHS")
    rhs = SelectField("RHS")