require 'sinatra'
require 'shotgun'
require 'sequel'
require 'fileutils'

Tilt.register Tilt::ERBTemplate, 'html.erb'

DB = Sequel.connect('postgres://diploma:diploma@localhost:5432/diploma')

get '/' do
  helicopters = DB[:helicopters].all
  criteria = DB[:criteria].order(:num).all
  # erb result.all.to_json
  erb :index, layout: :layout, locals: { helicopters: helicopters, criteria: criteria }
end

post '/get_result' do
  json = JSON.parse(request.body.read)
  method = json['method']
  groups = json['groups'].map { |g| g.split(', ').map { |a| a[1..-1].to_i - 1 } }
  coeffs = wrap json['coefficients']
  directions = wrap json['directions']
  params = groups.map { |g| wrap(g.join(',')) }.join(' ')
  timestamp = Time.now.utc.strftime("%Y%m%d%H%M%S")
  puts method
  puts coeffs
  puts directions
  puts params
  puts "python3 get_result.py #{timestamp} #{method} #{coeffs} #{directions} #{params}"
  logs_py = `python3 get_result.py #{timestamp} #{method} #{coeffs} #{directions} #{params}`
  file = "results/result#{timestamp}.xlsx"

  { file: file,
    logs_py: logs_py }.to_json
end

post '/upload' do
  p params
  tempfile = params['file']['tempfile']
  filename = File.join __dir__, 'public', 'uploads', "input#{timestamp = Time.now.utc.strftime("%Y%m%d%H%M%S")}.xlsx"
  File.open(filename, 'wb') { |f| f.write tempfile.read }

  logs_py = `python3 get_result_from_file.py #{timestamp} #{method}`
  file = "results/result#{timestamp}.xlsx"

  until File.exist? File.join __dir__, "public/#{file}"
    p 'waiting'
    sleep(1)
  end

  { file: file,
    logs_py: logs_py }.to_json
end

get '/get_template' do
  p __dir__
  p 'yes' if File.exist? File.join __dir__, 'public/results/result20220509210328.xlsx'
end

def wrap(s)
  "'#{s}'"
end