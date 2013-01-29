import commands
text = "This is a pen."
print commands.getoutput("ruby client.rb \"" + text + "\"")
