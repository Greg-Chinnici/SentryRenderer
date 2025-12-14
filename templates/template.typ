#let data = json("sentry.json")



#block[#repr(data)]

permalink 
#text(data.permalink)