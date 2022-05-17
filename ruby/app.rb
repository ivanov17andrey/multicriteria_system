require 'sinatra'
require 'shotgun'
require 'sequel'
require 'fileutils'

Tilt.register Tilt::ERBTemplate, 'html.erb'

DB = Sequel.connect('postgres://diploma:diploma@localhost:5432/diploma')

get '/' do
  helicopters = DB[:helicopters].all
  criteria = DB[:criteria].order(:num).all

  erb :index, layout: :layout, locals: { helicopters: helicopters, criteria: criteria }
end

post '/get_result' do
  json = JSON.parse(request.body.read)
  p json

  timestamp = Time.now.utc.strftime("%Y%m%d%H%M%S")
  method = json['method']
  alternatives_names = wrap json['alternatives_names']
  criteria_names = wrap json['criteria_names']
  estimates = wrap json['estimates']
  coeffs = wrap json['coefficients']
  directions = wrap json['directions']
  groups = wrap json['groups']

  logs_py = `python3 get_result.py #{timestamp} #{method} #{alternatives_names} #{criteria_names} #{estimates} #{coeffs} #{directions} #{groups}`
  file = "results/result#{timestamp}.xlsx"

  { file: file,
    logs_py: logs_py }.to_json
end

post '/upload' do
  timestamp = Time.now.utc.strftime("%Y%m%d%H%M%S")
  tempfile = params['file']['tempfile']
  filename = File.join __dir__, 'public', 'uploads', "input#{timestamp}.xlsx"
  File.open(filename, 'wb') { |f| f.write tempfile.read }

  method = params['method']
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
  "\"#{s}\""
end