import pandas as pd
from view.models import PaperTracking
from view.models import UserProfile
from view.models import Label

u = UserProfile.objects.get(pk=1)
a = pd.read_excel("/work/Research/PubMed-Mining/config/monitors.xlsx")

for _, i in a.iterrows():
    l = Label(user = u, name = i['label'])
    l.save()
    x = PaperTracking(user = u, type = i['type'], value = i['value'], label = l, memo = i['memo'])
    x.save()
