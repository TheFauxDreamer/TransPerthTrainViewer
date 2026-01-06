import requests
import json
from datetime import datetime
from urllib.parse import quote
import time

class TransperthLiveTimes:
    """Fetch live train times from Transperth API"""

    # Rate limiting configuration (in seconds)
    DELAY_BETWEEN_STATIONS = 18  # Delay between stations on same line
    DELAY_BETWEEN_LINES = 30     # Delay between different lines

    def __init__(self):
        self.base_url = "https://www.transperth.wa.gov.au"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-AU,en;q=0.9',
            'Referer': f'{self.base_url}/Timetables/Live-Train-Times',
            'X-Requested-With': 'XMLHttpRequest'
        })

        # Track rate limiting
        self.rate_limited_count = 0
        self.rate_limited_stations = []
        
        self.lines = {
            'airport': 'Airport Line',
            'armadale': 'Armadale Line',
            'ellenbrook': 'Ellenbrook Line',
            'fremantle': 'Fremantle Line',
            'mandurah': 'Mandurah Line',
            'midland': 'Midland Line',
            'thornlie': 'Thornlie-Cockburn Line',
            'yanchep': 'Yanchep Line'
        }
        
        # Station lists for each line (in order from terminus to Perth)
        self.line_stations = {
            'Yanchep Line': [
                'Yanchep Stn', 'Alkimos Stn', 'Eglinton Stn', 'Butler Stn', 
                'Clarkson Stn', 'Currambine Stn', 'Joondalup Stn', 'Edgewater Stn',
                'Whitfords Stn', 'Greenwood Stn', 'Warwick Stn', 'Stirling Stn',
                'Glendalough Stn', 'Leederville Stn', 'Perth Underground Stn', 'Elizabeth Quay Stn'
            ],
            'Mandurah Line': [
                'Mandurah Stn', 'Warnbro Stn', 'Rockingham Stn', 'Kwinana Stn',
                'Wellard Stn', 'Lakelands Stn', 'Warnbro Stn', 'Aubin Grove Stn',
                'Success Hill Stn', 'Cockburn Central Stn', 'Murdoch Stn', 'Bull Creek Stn',
                'Canning Bridge Stn', 'Elizabeth Quay Stn', 'Perth Underground Stn'
            ],
            'Fremantle Line': [
                'Fremantle Stn', 'North Fremantle Stn', 'Leighton Stn', 'Cottesloe Stn',
                'Grant Street Stn', 'Swanbourne Stn', 'Claremont Stn', 'Loch Street Stn',
                'Karrakatta Stn', 'City West Stn', 'Perth Underground Stn', 'McIver Stn'
            ],
            'Midland Line': [
                'Midland Stn', 'Woodbridge Stn', 'Guildford Stn', 'Bassendean Stn',
                'Ashfield Stn', 'Bayswater Stn', 'Meltham Stn', 'Maylands Stn',
                'Mount Lawley Stn', 'Perth Underground Stn', 'McIver Stn'
            ],
            'Armadale Line': [
                'Armadale Stn', 'Sherwood Stn', 'Seaforth Stn', 'Kelmscott Stn',
                'Challis Stn', 'Gosnells Stn', 'Maddington Stn', 'Beckenham Stn',
                'Cannington Stn', 'Queens Park Stn', 'Carlisle Stn', 'Oats Street Stn',
                'Victoria Park Stn', 'Burswood Stn', 'Perth Underground Stn', 'McIver Stn'
            ],
            'Ellenbrook Line': [
                'Ellenbrook Stn', 'Whiteman Park Stn', 'Bennett Springs West Stn',
                'Malaga Stn', 'Noranda Stn', 'Morley Stn', 'Bayswater Stn'
            ],
            'Airport Line': [
                'Airport Stn', 'Redcliffe Stn', 'Ashfield Stn', 'Bayswater Stn'
            ],
            'Thornlie-Cockburn Line': [
                'Thornlie Stn', 'Canning Vale Stn', 'Ranford Road Stn', 'Nicholson Road Stn',
                'Cockburn Central Stn'
            ]
        }
    
    def get_module_id(self):
        """Get the module ID from the page"""
        try:
            response = self.session.get(f"{self.base_url}/Timetables/Live-Train-Times")
            import re
            match = re.search(r'moduleId:\s*(\d+)', response.text)
            if match:
                return match.group(1)
            return "5111"
        except Exception as e:
            print(f"Warning: Could not get module ID: {e}")
            return "5111"
    
    def get_live_times(self, line, station):
        """Fetch live train times for a specific line and station"""
        module_id = self.get_module_id()
        api_url = f"{self.base_url}/API/TrainLiveTimes/LiveStatus/{quote(line)}/{quote(station)}"

        try:
            headers = {
                'ModuleId': module_id,
                'TabId': '248'
            }

            response = self.session.get(api_url, headers=headers)

            # Check for rate limiting (403 Forbidden)
            if response.status_code == 403:
                self.rate_limited_count += 1
                self.rate_limited_stations.append(f"{line} - {station}")
                print(f"\n[RATE LIMITED] at {station}!")
                print(f"The API returned 403 Forbidden - we're making requests too quickly.")
                print(f"Current delays: {self.DELAY_BETWEEN_STATIONS}s between stations, {self.DELAY_BETWEEN_LINES}s between lines")
                print(f"Consider increasing these values in the script.")
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                self.rate_limited_count += 1
                self.rate_limited_stations.append(f"{line} - {station}")
                print(f"\n[RATE LIMITED] at {station}!")
                print(f"The API returned 403 Forbidden - we're making requests too quickly.")
                print(f"Current delays: {self.DELAY_BETWEEN_STATIONS}s between stations, {self.DELAY_BETWEEN_LINES}s between lines")
                print(f"Consider increasing these values in the script.")
            else:
                print(f"HTTP Error fetching {station}: {e}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {station}: {e}")
            return None
    
    def get_all_stations_for_line(self, line_name):
        """Fetch live times for all stations on a line"""
        if line_name not in self.line_stations:
            print(f"Unknown line: {line_name}")
            return None

        stations = self.line_stations[line_name]
        all_data = {
            'line': line_name,
            'timestamp': datetime.now().strftime('%d/%m/%Y at %H:%M:%S'),
            'stations': {}
        }

        print(f"\nFetching data for {line_name}...")
        for i, station in enumerate(stations):
            print(f"  [{i+1}/{len(stations)}] Fetching {station}...")
            data = self.get_live_times(line_name, station)

            # Check if we got rate limited - stop immediately if so
            if self.rate_limited_count > 0:
                print(f"\n❌ Stopping fetch due to rate limiting")
                return None

            if data and data.get('result') == 'success':
                all_data['stations'][station] = data['data']
            else:
                all_data['stations'][station] = None

            # Be polite to the API
            time.sleep(self.DELAY_BETWEEN_STATIONS)

        return all_data
    
    def get_all_lines(self):
        """Fetch live times for all lines and all stations"""
        all_lines_data = {
            'timestamp': datetime.now().strftime('%d/%m/%Y at %H:%M:%S'),
            'lines': {}
        }

        line_names = list(self.line_stations.keys())
        for i, line_name in enumerate(line_names):
            line_data = self.get_all_stations_for_line(line_name)

            # Check if we got rate limited - stop immediately
            if self.rate_limited_count > 0:
                print(f"\n❌ Fetch aborted due to rate limiting")
                print(f"⏰ The API typically blocks requests for ~2 hours after rate limiting")
                print(f"💡 Please wait before trying again, or increase the delay values")
                break

            if line_data:
                all_lines_data['lines'][line_name] = line_data

            # Add delay between lines (except after the last line)
            if i < len(line_names) - 1:
                print(f"\n⏳ Waiting {self.DELAY_BETWEEN_LINES} seconds before fetching next line...")
                time.sleep(self.DELAY_BETWEEN_LINES)

        return all_lines_data

    def transform_to_train_centric(self, station_centric_data):
        """Transform station-centric data to train-centric format"""
        trains_dict = {}

        # Handle both multi-line format and single-line format
        if 'lines' in station_centric_data:
            # Multi-line format
            stations_to_process = []
            for line_name, line_data in station_centric_data['lines'].items():
                for station_name, station_data in line_data.get('stations', {}).items():
                    stations_to_process.append((station_name, station_data))
        elif 'stations' in station_centric_data:
            # Single-line format
            stations_to_process = list(station_centric_data['stations'].items())
        else:
            stations_to_process = []

        # Process all stations
        for station_name, station_data in stations_to_process:
            if not station_data or 'StatusDetailList' not in station_data:
                continue

            # Process each train at this station
            for train_info in station_data['StatusDetailList']:
                # Support both TrainID and TripId
                train_id = train_info.get('TrainID') or train_info.get('TripId')
                if not train_id:
                    continue

                train_id = str(train_id)  # Ensure it's a string

                # If first time seeing this train, create entry with metadata
                if train_id not in trains_dict:
                    trains_dict[train_id] = {
                        'id': train_id,
                        'line': train_info.get('LineName', ''),
                        'destination': train_info.get('Destination', ''),
                        'platform': train_info.get('Platform', ''),
                        'ncar': train_info.get('Ncar', ''),
                        'series': train_info.get('Series', ''),
                        'status': train_info.get('StatusDetail', ''),
                        'stops': []
                    }

                # Add this station stop
                trains_dict[train_id]['stops'].append({
                    'station': station_name,
                    'time': train_info.get('Departure', '')
                })

        # Sort stops by time for each train
        for train in trains_dict.values():
            train['stops'].sort(key=lambda x: x['time'])

        return {
            'timestamp': station_centric_data.get('timestamp', ''),
            'trains': trains_dict
        }


# Example usage
if __name__ == "__main__":
    fetcher = TransperthLiveTimes()

    print("=" * 70)
    print("Fetching ALL LINES data...")
    print(f"Rate limiting: {fetcher.DELAY_BETWEEN_STATIONS}s between stations, "
          f"{fetcher.DELAY_BETWEEN_LINES}s between lines")
    print("=" * 70)

    # Fetch station-centric data
    station_data = fetcher.get_all_lines()

    # Transform to train-centric format
    print("\n🔄 Transforming to train-centric format...")
    train_data = fetcher.transform_to_train_centric(station_data)

    # Save train-centric format (optimized)
    with open('live_train_map.json', 'w') as f:
        json.dump(train_data, f, indent=2)

    print("\n" + "=" * 70)
    print("✓ Optimized train data saved to live_train_map.json")
    print("=" * 70)

    # Print summary
    import os
    file_size = os.path.getsize('live_train_map.json') / 1024
    train_count = len(train_data['trains'])
    print(f"\nSummary:")
    print(f"{'='*70}")
    print(f"  Trains: {train_count}")
    print(f"  File size: {file_size:.1f} KB")
    if train_count > 0:
        avg_stops = sum(len(t['stops']) for t in train_data['trains'].values()) / train_count
        print(f"  Average stops per train: {avg_stops:.1f}")

    # Rate limiting report
    if fetcher.rate_limited_count > 0:
        print(f"\n⚠️  Rate Limiting Report:")
        print(f"{'='*70}")
        print(f"  Times rate limited: {fetcher.rate_limited_count}")
        print(f"  Stations affected:")
        for station in fetcher.rate_limited_stations[:10]:  # Show first 10
            print(f"    - {station}")
        if len(fetcher.rate_limited_stations) > 10:
            print(f"    ... and {len(fetcher.rate_limited_stations) - 10} more")
        print(f"\n  Recommendation: Increase delays to:")
        print(f"    DELAY_BETWEEN_STATIONS = {fetcher.DELAY_BETWEEN_STATIONS + 5}s  (currently {fetcher.DELAY_BETWEEN_STATIONS}s)")
        print(f"    DELAY_BETWEEN_LINES = {fetcher.DELAY_BETWEEN_LINES + 10}s  (currently {fetcher.DELAY_BETWEEN_LINES}s)")
    else:
        print(f"\n✓ No rate limiting detected - current delays are working well!")
    print(f"{'='*70}")
