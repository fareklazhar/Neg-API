require "socket"

TCPSocket.open("localhost", 7070) do |socket|
  socket.puts ARGV[0]
  puts socket.gets#.gsub(" ", "\n").chomp
end
