import os
import pandas as pd
from django.core.management.base import BaseCommand
from colleges.models import College

class Command(BaseCommand):
    help = 'Import colleges data from Top CSV files'

    def get_state_code(self, state_name):
        """Convert state name to state code"""
        state_mapping = {
            'ANDAMAN AND NICOBAR ISLANDS': 'AN',
            'ANDHRA PRADESH': 'AP',
            'ARUNACHAL PRADESH': 'AR',
            'ASSAM': 'AS',
            'BIHAR': 'BR',
            'CHANDIGARH': 'CH',
            'CHHATTISGARH': 'CT',
            'DADRA AND NAGAR HAVELI': 'DN',
            'DAMAN AND DIU': 'DD',
            'DELHI': 'DL',
            'GOA': 'GA',
            'GUJARAT': 'GJ',
            'HARYANA': 'HR',
            'HIMACHAL PRADESH': 'HP',
            'JAMMU AND KASHMIR': 'JK',
            'JHARKHAND': 'JH',
            'KARNATAKA': 'KA',
            'KERALA': 'KL',
            'LADAKH': 'LA',
            'LAKSHADWEEP': 'LD',
            'MADHYA PRADESH': 'MP',
            'MAHARASHTRA': 'MH',
            'MANIPUR': 'MN',
            'MEGHALAYA': 'ML',
            'MIZORAM': 'MZ',
            'NAGALAND': 'NL',
            'ODISHA': 'OR',
            'PUDUCHERRY': 'PY',
            'PUNJAB': 'PB',
            'RAJASTHAN': 'RJ',
            'SIKKIM': 'SK',
            'TAMIL NADU': 'TN',
            'TELANGANA': 'TG',
            'TRIPURA': 'TR',
            'UTTAR PRADESH': 'UP',
            'UTTARAKHAND': 'UT',
            'WEST BENGAL': 'WB',
            # Add common variations
            'NEW DELHI': 'DL',
            'NCT OF DELHI': 'DL',
            'ORISSA': 'OR',
            'PONDICHERRY': 'PY',
            'UTTARANCHAL': 'UT',
            'TAMILNADU': 'TN',
            'ANDHRA': 'AP',
            'UP': 'UP',
            'AP': 'AP',
            'MP': 'MP',
            # Add medical data variations
            'DELHI': 'DL',
            'TAMIL NADU': 'TN',
            'PONDICHERRY': 'PY',
            'GUJARAT': 'GJ',
        }
        
        if not isinstance(state_name, str):
            return None
            
        state_name = state_name.strip().upper()
        return state_mapping.get(state_name)

    def standardize_category(self, filename):
        """Convert filename to standard category name"""
        category_mapping = {
            'Engineering': 'eng',
            'Medical': 'medical',
            'Dental': 'dental',
            'Pharmacy': 'pharmacy',
            'Law': 'law',
            'Management': 'management',
            'Architecture & Planning': 'architecture',
            'Architecture & Plann': 'architecture',
            'Architecture': 'architecture',
        }
        
        # Extract category from filename (e.g., "Top 100 in Engineering.csv" -> "Engineering")
        category = filename.split('in')[1].split('.')[0].strip()
        
        # Map the category to the correct database value
        return category_mapping.get(category.strip(), category.lower())

    def clean_medical_data(self, df):
        """Clean and deduplicate medical college data"""
        # Remove rows where Name is NaN or contains 'Name'
        df = df.dropna(subset=['Name'])
        df = df[~df['Name'].str.contains('Name', na=False)]
        
        # Drop duplicates based on Name
        df = df.drop_duplicates(subset=['Name'], keep='first')
        
        return df

    def handle(self, *args, **kwargs):
        # Clear existing data
        College.objects.all().delete()
        self.stdout.write('Cleared existing college data')

        data_dir = 'datas'
        # Get all CSV files
        files = [f for f in os.listdir(data_dir) 
                if f.startswith('Top') and f.endswith('.csv')]

        for filename in files:
            try:
                category = self.standardize_category(filename)
                self.stdout.write(f'\nProcessing {filename}...')
                
                file_path = os.path.join(data_dir, filename)
                df = pd.read_csv(file_path)
                
                # Special handling for medical data
                if 'Medical' in filename:
                    df = self.clean_medical_data(df)
                
                for index, row in df.iterrows():
                    try:
                        # Get and validate name
                        name = str(row.get('Name', '')).strip()
                        if not name or pd.isna(name):
                            self.stdout.write(
                                self.style.WARNING(f'Row {index + 1}: Empty or invalid name, skipping')
                            )
                            continue

                        # Get city and state directly from columns
                        city = str(row.get('City', '')).strip()
                        state = row.get('State', '')
                        state_code = self.get_state_code(state)
                        
                        if not state_code:
                            self.stdout.write(
                                self.style.WARNING(f'Row {index + 1}: Invalid state "{state}" for college "{name}", skipping')
                            )
                            continue

                        # Get ranking - handle both 'Rank' and 'ranking' columns
                        rank = row.get('Rank', row.get('ranking'))
                        if pd.isna(rank):
                            rank = None

                        # Create college entry
                        college = College.objects.create(
                            name=name,
                            category=category,
                            city=city,
                            state=state_code,
                            ranking=rank,
                            website=str(row.get('Website', '')),
                            established=row.get('Established'),
                            ownership=str(row.get('Ownership', '')),
                            approved_by=str(row.get('Approved By', '')),
                            affiliated_to=str(row.get('Affiliated to', '')),
                            facilities=str(row.get('Facilities', '')),
                            courses_offered=str(row.get('Courses', ''))
                        )
                        self.stdout.write(f'Successfully imported: {name}')
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Error importing row {index + 1}: {str(e)}')
                        )
                        continue

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing file {filename}: {str(e)}')
                )
                continue

        self.stdout.write(self.style.SUCCESS('Successfully imported all college data')) 