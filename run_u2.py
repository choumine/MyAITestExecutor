import uiautomator2 as u2

d = u2.connect() # connect to device
# print(d.dump_hierarchy())
d.xpath("//*[@resource-id='com.android.contacts:id/one']").click()