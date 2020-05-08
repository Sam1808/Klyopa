import argparse
import random
import speedtest
import requests
from requests.exceptions import ConnectionError
from ping3 import ping
from terminaltables import SingleTable
from statistics import mean, median

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

    print(f'''Total tests: {len(closest_test_servers)}''')

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

def buid_html_table(result,table): #need to review
    html_data = '<table width="60%" border="1" align="center"><tr><td>'+str(result)+'</td></tr>'
    for data in table:
        html_data = html_data+'<tr>'
        for detail in data:
            html_data = html_data + '<td>'+str(detail)+'</td>'
        html_data = html_data + '</tr>'
    return html_data+'</table><br><br>'

def render_progressbar(total, iteration, prefix='', suffix='', length=30, fill='█', zfill='░'):
  iteration = min(total, iteration)
  percent = "{0:.1f}"
  percent = percent.format(100 * (iteration / float(total)))
  filled_length = int(length * iteration // total)
  pbar = fill * filled_length + zfill * (length - filled_length)
  return '{0} |{1}| {2}% {3}'.format(prefix, pbar, percent, suffix)


def make_icmp_test(node, number_of_tests, packet_size):
    icmp_results = []
    lost_packets = 0
    for number in range(0, number_of_tests):
        print(render_progressbar(number_of_tests,number+1),end='\r', flush=True)
        icmp_test = ping(node, unit='ms', size=packet_size)
        if not icmp_test:
            lost_packets += 1
            continue
        icmp_results.append(icmp_test)
    return icmp_results, lost_packets

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Klyopa. Let`s test provider connection!')
    parser.add_argument('--node', help='Provider node for icmp test (root rights)')
    parser.add_argument('--number_of_tests', type=int, default=10000, help='Number of icmp reqests (default: 10000)')
    parser.add_argument('--packet_size', type=int, default=996, help='Set ICMP packet payload (default: 996)')
    parser.add_argument('--server_mode', help='Speedtest(c) mini server mode')
    parser.add_argument('--ratio_of_global_tests', type=int, default=3, help='Global test ratio (default ratio 3, total 9 tests for each type)')

    args = parser.parse_args()

    node = args.node
    packet_size = args.packet_size
    number_of_tests = args.number_of_tests

    if not args.server_mode:
        # --------start TESTS -------

        try:
            response = requests.get('http://google.com', allow_redirects=False)
            response.raise_for_status()
        except ConnectionError:
            print(f'''
            Cannot find google.com.
            Connection Error: Please check your Internet connection (include DNS) and try again.
            ''')
            exit()

    # --------end TESTS -------

    s = speedtest.Speedtest()
    user_config = s.get_config()
    your_ip = user_config["client"]["ip"]
    your_country = user_config["client"]["country"]


    print(f'''
                                           -.  --                       
        -= KLYOPA =-                     -      :                      
        ver.1.1 alfa                     -        :.                    
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

    if node:

        # --Start tests

        if packet_size > 996:
            print(f'There is no way to use packet size more than 996 bytes by design. Please try again.')
            exit()

        try:
            resolve = ping(node)
        except PermissionError:
            print('Permission Error. For icmp tests you need Administrator (root) rights.')
            exit()

        if not resolve:
            print(f'Cannot resolve {node}. Please check provider node and try again.')
            exit()



        # --End tests

        print(f'Run icmp tests with {node}. Progress:')
        icmp_results, lost_packets = make_icmp_test(node, number_of_tests, packet_size)
        print('''
        ''')
        percent_lost = round(lost_packets * 100 / number_of_tests, 2)

        icmp_results_consolidated = {}
        icmp_results_consolidated['Provider node'] = node
        icmp_results_consolidated['Packet size (bytes)'] = packet_size
        icmp_results_consolidated['Total packets send'] = number_of_tests
        icmp_results_consolidated['Packets are received'] = len(icmp_results)
        icmp_results_consolidated['Packets are received (%)'] = 100 - percent_lost
        icmp_results_consolidated['Packets are lost'] = lost_packets
        icmp_results_consolidated['Packets are lost (%)'] = percent_lost
        icmp_results_consolidated['Max value (ms)'] = round(max(icmp_results), 2)
        icmp_results_consolidated['Average value (ms)'] = round(mean(icmp_results), 2)
        icmp_results_consolidated['Median value (ms)'] = round(median(icmp_results), 2)
        icmp_results_consolidated['Min value (ms)'] = round(min(icmp_results), 2)
        icmp_results_consolidated['Jitter (ms)'] = round(max(icmp_results) - min(icmp_results), 2)

        icmp_table = [['Specification', 'Results']]
        for key in icmp_results_consolidated:
            icmp_table.append([key, icmp_results_consolidated[key]])
        build_table('Icmp tests', icmp_table)




    ratio_of_global_tests = args.ratio_of_global_tests
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

    print(f'''Test complete.
        
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

    mbit_factor = 0.000001 #bits to Mbit factor
    html_code =''
    if icmp_table:
        html_code = f'{html_code} {buid_html_table("Icmp tests", icmp_table)}'
    for result in general_results:
        table_data = [['Country', 'Location', 'Provider', 'Ping ms', 'Upload Mbps', 'Download Mbps']]
        result_tests = general_results[result]
        for test in result_tests:
            results_table = [test['server']['country'],test['server']['name'],test['server']['sponsor'],test['ping'],round(test['upload']*mbit_factor, 2),round(test['download']*mbit_factor, 2)]
            table_data.append(results_table)
        build_table(result,table_data)
        html_code = f'{html_code} {buid_html_table(result,table_data)}'
        print()

    with open('report.html', 'w') as html_file:
        html_file.write(html_code)

    input('Please check report.html file. Press [Enter] to exit')
