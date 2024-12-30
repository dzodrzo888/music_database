import asyncio
import aiohttp
import logging
import json
from statistics import mean
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

base_path = Path(__file__).resolve().parent.parent.parent.parent
env_path = base_path / 'env_files' / 'ai_db_detail.env'
log_dir = base_path / 'logger'
log_file = log_dir / 'app.log'

load_dotenv(dotenv_path=env_path)

sys.path.append(str(base_path))

from backend.database_manager.database_manager import DatabaseManager

# Logger setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AcousticBrainzFetcher:

    def __init__(self, cursor, db_manager):
        self.base_url = "https://acousticbrainz.org"
        self.cursor = cursor
        self.db_manager = db_manager

    async def fetch_features_batch(self, session, mbids):
        """
        Fetch features for a batch of MBIDs asynchronously.
        """
        tasks = []
        results = []

        for idx, mbid in enumerate(mbids):
            tasks.append(self.fetch_single_features(session, mbid))

            if (idx + 1) % 10 == 0:
                logger.info(f"Sleeping for 10 seconds to respect API rate limits after {idx + 1} requests.")
                results.extend(await asyncio.gather(*tasks, return_exceptions=True))
                tasks = []  
                await asyncio.sleep(10)  

        if tasks:
            results.extend(await asyncio.gather(*tasks, return_exceptions=True))

        return [res for res in results if res]

    async def fetch_single_features(self, session, mbid):
        """
        Fetch high-level and low-level features for a single MBID.
        """
        features = {"mbid": mbid}
        try:
            async with session.get(f"{self.base_url}/{mbid}/high-level") as response_high:
                response_high.raise_for_status()
                high_data = await response_high.json()
                features["high_level"] = self.extract_high_level_features(high_data)

            async with session.get(f"{self.base_url}/{mbid}/low-level") as response_low:
                response_low.raise_for_status()
                low_data = await response_low.json()
                features["low_level"] = self.extract_low_level_features(low_data)
        except Exception as e:
            logger.error(f"Error fetching features for MBID {mbid}: {e}")
            return None
        return features

    def extract_high_level_features(self, data):
        """
        Extract high-level features.
        """
        high_level = data.get('highlevel', {})
        features = {key: high_level.get(key, {}).get('value', None) for key in high_level}
        return json.dumps(features)

    def extract_low_level_features(self, data):
        """
        Extract low-level features.
        """
        features = {}
        for key, key_dict in data.items():
            for feature, values in key_dict.items():
                if isinstance(values, dict) and 'mean' in values:
                    features[feature] = mean(values['mean']) if isinstance(values['mean'], list) else values['mean']
                elif isinstance(values, (str, float, int)):
                    features[feature] = values
        return json.dumps(features)

    def batch_insert_tracks(self, track_infos):
        """
        Batch insert tracks into the database.
        """
        try:
            placeholders = ", ".join(["%s"] * len(track_infos[0]))
            columns = ", ".join(track_infos[0].keys())
            query = f"""
                INSERT INTO `Track_info`({columns})
                VALUES ({placeholders})
            """
            values = [tuple(track.values()) for track in track_infos]
            self.cursor.executemany(query, values)
            self.db_manager.commit()
            logger.info(f"Inserted batch of {len(track_infos)} tracks successfully.")
        except Exception as e:
            logger.error(f"Error inserting tracks: {e}")

async def main():

    db_config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    db_manager = DatabaseManager(db_config=db_config)
    cursor = db_manager.get_cursor()

    cursor.execute("SELECT mbid FROM Tracks;")
    mbids = [row['mbid'] for row in cursor.fetchall()]

    fetcher = AcousticBrainzFetcher(cursor, db_manager)
    batch_size = 25  

    all_features = []

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(mbids), batch_size):
            batch = mbids[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}/{len(mbids) // batch_size + 1}")
            features_batch = await fetcher.fetch_features_batch(session, batch)
            all_features.extend(features_batch)

            if len(all_features) >= 100:
                fetcher.batch_insert_tracks(all_features)
                all_features = [] 

        if all_features:
            fetcher.batch_insert_tracks(all_features)

if __name__ == "__main__":
    asyncio.run(main())