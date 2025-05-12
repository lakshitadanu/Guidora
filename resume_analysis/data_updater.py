import requests
import json
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
from datetime import datetime
import logging
import os

class IndustryDataCollector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_path = 'resume_analysis/data'
        
    def fetch_onet_data(self, api_key):
        """
        Fetch comprehensive occupation data from O*NET API
        """
        base_url = "https://services.onetcenter.org/ws/online/occupations"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            response = requests.get(base_url, headers=headers)
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching O*NET data: {str(e)}")
            return None

    def fetch_bls_data(self, api_key):
        """
        Fetch employment statistics and projections from Bureau of Labor Statistics
        """
        base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        headers = {"Content-type": "application/json"}
        
        try:
            response = requests.get(base_url, headers=headers)
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching BLS data: {str(e)}")
            return None

    def scrape_job_boards(self):
        """
        Scrape job postings from major job boards
        """
        job_sites = {
            'indeed': 'https://www.indeed.com/jobs?q=',
            'linkedin': 'https://www.linkedin.com/jobs/search?keywords=',
            'glassdoor': 'https://www.glassdoor.com/Job/jobs.htm?sc.keyword='
        }
        
        job_data = []
        
        for site, base_url in job_sites.items():
            try:
                # Add different job categories to search
                for category in ['technology', 'healthcare', 'finance', 'marketing']:
                    url = base_url + category
                    response = requests.get(url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    job_data.extend(self._parse_job_listings(soup, site))
            except Exception as e:
                self.logger.error(f"Error scraping {site}: {str(e)}")
                
        return job_data

    def _parse_job_listings(self, soup, site):
        """
        Parse job listings based on the specific structure of each job board
        """
        listings = []
        
        if site == 'indeed':
            jobs = soup.find_all('div', class_='jobsearch-SerpJobCard')
            for job in jobs:
                listings.append({
                    'title': job.find('h2', class_='title').text.strip(),
                    'company': job.find('span', class_='company').text.strip(),
                    'description': job.find('div', class_='summary').text.strip(),
                    'source': 'indeed'
                })
        # Add parsing for other job sites
        
        return listings

    def extract_skills_and_trends(self, job_data):
        """
        Use NLP to extract skills and trends from job postings
        """
        # Combine all job descriptions
        descriptions = [job['description'] for job in job_data]
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(descriptions)
        
        # Cluster job postings
        kmeans = KMeans(n_clusters=10, random_state=42)
        clusters = kmeans.fit_predict(tfidf_matrix)
        
        # Extract top terms for each cluster
        feature_names = vectorizer.get_feature_names_out()
        trends = self._extract_cluster_trends(kmeans, feature_names)
        
        return trends

    def _extract_cluster_trends(self, kmeans, feature_names):
        """
        Extract trending terms from each cluster
        """
        trends = {}
        
        for i in range(kmeans.n_clusters):
            # Get top terms for this cluster
            order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
            terms = [feature_names[ind] for ind in order_centroids[i, :10]]
            
            trends[f'cluster_{i}'] = {
                'top_terms': terms,
                'trend_score': float(kmeans.cluster_centers_[i].max())
            }
            
        return trends

    def update_data_files(self):
        """
        Update skills.json and industry_trends.json with new data
        """
        try:
            # Collect data from various sources
            onet_data = self.fetch_onet_data(os.getenv('ONET_API_KEY'))
            bls_data = self.fetch_bls_data(os.getenv('BLS_API_KEY'))
            job_data = self.scrape_job_boards()
            
            # Extract trends and insights
            trends = self.extract_skills_and_trends(job_data)
            
            # Update skills.json
            skills_data = self._generate_skills_data(onet_data, job_data)
            with open(f'{self.base_path}/skills.json', 'w') as f:
                json.dump(skills_data, f, indent=4)
            
            # Update industry_trends.json
            trends_data = self._generate_trends_data(bls_data, trends)
            with open(f'{self.base_path}/industry_trends.json', 'w') as f:
                json.dump(trends_data, f, indent=4)
            
            # Log successful update
            self.logger.info(f"Data files updated successfully at {datetime.now()}")
            
        except Exception as e:
            self.logger.error(f"Error updating data files: {str(e)}")

    def _generate_skills_data(self, onet_data, job_data):
        """
        Generate structured skills data from O*NET and job postings
        """
        skills_data = {}
        
        # Process O*NET skills data
        if onet_data:
            for occupation in onet_data['occupations']:
                category = occupation.get('category', 'Other')
                if category not in skills_data:
                    skills_data[category] = []
                skills_data[category].extend(occupation.get('skills', []))
        
        # Add skills from job postings
        job_skills = self._extract_skills_from_jobs(job_data)
        for category, skills in job_skills.items():
            if category in skills_data:
                skills_data[category].extend(skills)
            else:
                skills_data[category] = skills
        
        # Remove duplicates and sort
        for category in skills_data:
            skills_data[category] = sorted(list(set(skills_data[category])))
        
        return skills_data

    def _generate_trends_data(self, bls_data, trends):
        """
        Generate industry trends data from BLS statistics and analyzed trends
        """
        trends_data = {}
        
        # Process BLS employment projections
        if bls_data:
            for industry in bls_data.get('Results', {}).get('series', []):
                category = industry.get('industry_name')
                if category:
                    trends_data[category] = {
                        'growth_rate': industry.get('growth_rate'),
                        'employment_change': industry.get('employment_change'),
                        'median_wage': industry.get('median_wage')
                    }
        
        # Add trending roles and skills from analysis
        for cluster, data in trends.items():
            category = self._map_cluster_to_category(cluster, data['top_terms'])
            if category in trends_data:
                trends_data[category].update({
                    'trending_roles': data['top_terms'][:5],
                    'key_skills': data['top_terms'][5:10]
                })
        
        return trends_data

    def _map_cluster_to_category(self, cluster, terms):
        """
        Map a cluster to an industry category based on its terms
        """
        # Implement logic to map clusters to categories
        # This could use keyword matching or more sophisticated NLP
        return "Category"  # Placeholder

    def _extract_skills_from_jobs(self, job_data):
        """
        Extract skills mentioned in job postings
        """
        skills = defaultdict(set)
        
        # Implement skill extraction logic
        # Could use named entity recognition or keyword matching
        
        return dict(skills)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize and run the collector
    collector = IndustryDataCollector()
    collector.update_data_files() 