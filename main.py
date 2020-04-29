import random
import speedtest
from fpdf import FPDF, HTMLMixin # pdf creator
from terminaltables import AsciiTable, DoubleTable, SingleTable

class HTML2PDF(FPDF, HTMLMixin): # html to pdf
    pass

def get_speedtest_results(test_servers):
    results = []
    for server in test_servers:
        s = speedtest.Speedtest()
        s.get_servers([server])
        s.download()
        s.upload(pre_allocate=False)
        results.append(s.results.dict())
        print(f'Server ID: {server} - test OK')
    return results

def get_closest_servers_results():

    closest_servers = s.get_closest_servers()
    countries_code_catalog = []
    for server in closest_servers:
        countries_code_catalog.append(server.get('cc'))
    unique_countries_code_catalog = set(countries_code_catalog)

    servers_glossary = {}

    for country_code in unique_countries_code_catalog:
        one_country_code_servers = []
        for server in closest_servers:
            if country_code == server.get('cc'):
                one_country_code_servers.append(server.get('id'))
        servers_glossary[country_code] = one_country_code_servers

    closest_test_servers = []

    for country_code in servers_glossary:
        one_country_test_servers_ids = servers_glossary[country_code]
        existing_servers = len(one_country_test_servers_ids) >= 1
        if existing_servers:
            one_country_test_server_id = one_country_test_servers_ids[
            random.randint(0, len(one_country_test_servers_ids) - 1)]
            closest_test_servers.append(one_country_test_server_id)

    print(f'''
        Total tests: {len(closest_test_servers)}
        ''')

    return get_speedtest_results(closest_test_servers)

def get_servers_catalogs(your_country):
    all_servers_raw = s.get_servers()
    all_servers = list(all_servers_raw.values())
    test_servers_local = []
    test_servers_world_wide = []
    for server in all_servers:
        if your_country == server[0]['cc'] or your_country == server[0]['country']:
            test_servers_local.append(server[0]['id'])
        else:
            test_servers_world_wide.append(server[0]['id'])
    return test_servers_local,test_servers_world_wide

def build_table(title, table_data):

    table_instance = SingleTable(table_data, title)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)

def buid_html_table(table):
    html_data = '<table width="100%" border="1" align="center">'
    for data in table:
        html_data = html_data+'<tr>'
        for detail in data:
            html_data = html_data + '<th width="15%"><font size="8">'+str(detail)+'</font></th>'
        html_data = html_data + '</tr>'
    return html_data+'</table>'

if __name__ == '__main__':

    s = speedtest.Speedtest()
    user_config = s.get_config()
    your_ip = user_config["client"]["ip"]
    your_country = user_config["client"]["country"]


    print(f'''
                                           -.  --                       
        -= KLYOPA =-                     -      :                      
                                         -        :.                    
        Internet speed test.             -         :                    
                                        .          .-                   
             :.   -:.                  -.          .:                   
             :       :.                :            :                   
             :.        .-             -   -        - :                  
              :          .-  .-::....  ....:.:    -- -                  
              -.         - -..             .:--.-.:  -                  
               -.        :.                  ...:-- -.                  
                -       .-.           :*-..:. ..   ..                   
                ..     ..:            +: . -.  .  .                     
                ..   -::* :*::        ....-:-  .. -                     
                 --  .-:.: -.:-                ..:                      
                   -: .....-.   -  .:          ..-                      
                     -:-:-      .. -      -.  :..:                      
Service provided by      .-.      ..      ..::. .-                      
   OOKLA                  .--     .:..... -..    -                      
www.speedtest.net           :.----.     .--                             
                           -.     .-:::-.                               
                                                                        
              
        IP: {your_ip}
        Provider: {user_config["client"]["isp"]}
        Country: {your_country}
        ''')
    ratio_of_global_tests = 1
    general_results = {}

    best_test_server = s.get_best_server()
    print(f'''
        Get test with best test server:
        Location: {best_test_server['name']}
        Provider: {best_test_server['sponsor']}
        Country:  {best_test_server['country']}
        ''')
    s.upload(pre_allocate=False)
    s.download()
    general_results['best_server'] = [s.results.dict()]

    print(f'''
        Get tests with closest servers.
        ''')
    general_results['closest_servers'] = get_closest_servers_results()

    print(f'''
        Get {ratio_of_global_tests*3} tests with local servers.
        ''')

    local_servers_catalog, world_wide_servers_catalog = get_servers_catalogs(your_country)
    general_results['closest_local_servers'] = get_speedtest_results(local_servers_catalog[:ratio_of_global_tests])
    local_servers_middle_index = int(len(local_servers_catalog) / 2)
    general_results['middle_local_servers'] = get_speedtest_results(
        local_servers_catalog[local_servers_middle_index:local_servers_middle_index+ratio_of_global_tests])
    general_results['far_from_local_servers'] = get_speedtest_results(local_servers_catalog[-ratio_of_global_tests:])

    print(f'''
        Get {ratio_of_global_tests*3} tests with word wide servers.
        ''')
    general_results['closest_word_wide_servers'] = get_speedtest_results(world_wide_servers_catalog[:ratio_of_global_tests])
    ww_servers_middle_index = int(len(world_wide_servers_catalog) / 2)
    general_results['middle_word_wide_servers'] = get_speedtest_results(
        world_wide_servers_catalog[ww_servers_middle_index:ww_servers_middle_index+ratio_of_global_tests])
    general_results['far_from_world_wide_servers'] = get_speedtest_results(world_wide_servers_catalog[-ratio_of_global_tests:])

    print(f'''
        Results:
        ''')

    mib_factor = 1048576 #bytes to MiB factor
    html_code =''
    for result in general_results:
        table_data = [['Country', 'Location', 'Provider', 'Ping ms', 'Upload MiB', 'Download MiB']]
        result_tests = general_results[result]
        for test in result_tests:
            results_table = [test['server']['country'],test['server']['name'],test['server']['sponsor'],test['ping'],round(test['upload']/mib_factor, 2),round(test['download']/mib_factor, 2)]
            table_data.append(results_table)
        build_table(result,table_data)
        html_code = f'{html_code} {buid_html_table(table_data)}'
        print()
    pdf = HTML2PDF()
    pdf.add_page()
    pdf.write_html(html_code)

    pdf.output('report.pdf')
