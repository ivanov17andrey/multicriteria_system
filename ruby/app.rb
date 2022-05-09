require 'sinatra'
require 'shotgun'
require 'sequel'

Tilt.register Tilt::ERBTemplate, 'html.erb'

DB = Sequel.connect('postgres://diploma:diploma@localhost:5432/diploma')

get '/' do
  helicopters = DB[:helicopters].all
  criteria = DB[:criteria].order(:num).all
  # erb result.all.to_json
  erb :index, layout: :layout, locals: { helicopters: helicopters, criteria: criteria }
end

post '/get_table' do
  json = JSON.parse(request.body.read)
  groups = json['groups'].map { |g| g.split(', ').map { |a| a[1..-1].to_i - 1 } }
  coeffs = wrap json['coefficients']
  params = groups.map { |g| wrap(g.join(',')) }.join(' ')
  timestamp = Time.now.utc.strftime("%Y%m%d%H%M%S")
  puts coeffs
  puts params
  puts "python3 get_table.py #{timestamp} #{coeffs} #{params}"
  `python3 get_table.py #{timestamp} #{coeffs} #{params}`

  file = "result#{timestamp}.xlsx"
  {file: file}.to_json
end

def wrap(s)
  "'#{s}'"
end