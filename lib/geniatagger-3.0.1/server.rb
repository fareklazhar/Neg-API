require "webrick"

def readlines_until_empty_line(io)
  result = []
  while line = io.gets
    break if line == "\n"
    result << line
  end
  result
end

genia = IO.popen("./geniatagger 2>/dev/null", "r+")

server = WEBrick::GenericServer.new(:Port => 7070)
trap(:INT) do
  server.shutdown
  genia.close
end
server.start do |socket|
  puts "RR"
  while line = socket.gets
    puts line
    genia.print line
    socket.print readlines_until_empty_line(genia).join.gsub("\n", " "), "\n"
  end
  puts "AA"
end
