"""
Google Sheets CSV Reader Service for Virtual Events

This service handles reading data from public Google Sheets using CSV export URLs.
It properly handles the spreadsheet structure with 3 header rows to skip.
"""

import os
import pandas as pd
import requests
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Service for reading data from Google Sheets via CSV export"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Voluntold-VirtualEvents/1.0'
        })
    
    def read_sheet_data(self, sheet_id: str) -> List[Dict]:
        """
        Read data from a Google Sheet and return as list of dictionaries.
        
        Args:
            sheet_id (str): Google Sheet ID from the URL
            
        Returns:
            List[Dict]: List of dictionaries representing sheet rows
            
        Raises:
            ValueError: If sheet_id is not provided
            ConnectionError: If unable to connect to Google Sheets
            Exception: For other errors during data processing
        """
        if not sheet_id:
            raise ValueError("Sheet ID is required")
        
        # Try primary URL format first
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
        
        try:
            logger.info(f"Attempting to fetch sheet with ID: {sheet_id}")
            logger.info(f"Primary URL: {csv_url}")
            
            df = pd.read_csv(csv_url)
            
        except Exception as e:
            logger.warning(f"Primary URL failed: {str(e)}")
            # Try fallback URL format
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            logger.info(f"Trying fallback URL: {csv_url}")
            
            try:
                df = pd.read_csv(csv_url)
            except Exception as e2:
                logger.error(f"Both URL formats failed. Primary: {str(e)}, Fallback: {str(e2)}")
                raise ConnectionError(f"Unable to connect to Google Sheet {sheet_id}: {str(e2)}")
        
        logger.info(f"Successfully loaded CSV with {len(df)} rows")
        
        # Skip first 3 rows (header information) as per spreadsheet structure
        if len(df) > 3:
            df = df.iloc[3:].reset_index(drop=True)
            logger.info(f"After skipping 3 header rows: {len(df)} data rows")
        else:
            logger.warning("Sheet has 3 or fewer rows - no data rows found")
            return []
        
        # Clean column names - extract the actual column name from mixed header text
        # We need to be more specific to avoid duplicate column names
        cleaned_columns = {}
        column_mapping = {
            'Status': 'Status',
            'Date': 'Date', 
            'Time': 'Time',
            'Session Type': 'Session Type',
            'Teacher Name': 'Teacher Name',
            'School Name': 'School Name',
            'School Level': 'School Level',
            'District': 'District',
            'Session Title': 'Session Title',
            'Presenter': 'Presenter',
            'Organization': 'Organization',
            'Presenter Location': 'Presenter Location',
            'Topic/Theme': 'Topic/Theme',
            'Session Link': 'Session Link'
        }
        
        # Find the correct column for each expected field
        for expected_col, target_name in column_mapping.items():
            for col in df.columns:
                if expected_col in col and col != target_name:
                    # Only rename if we haven't already found this column
                    if target_name not in cleaned_columns.values():
                        cleaned_columns[col] = target_name
                        break
        
        # Rename columns
        if cleaned_columns:
            df = df.rename(columns=cleaned_columns)
            logger.info(f"Cleaned column names: {list(cleaned_columns.values())}")
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        # Clean up the data - handle NaN values and empty strings
        cleaned_data = []
        for row in data:
            cleaned_row = {}
            for key, value in row.items():
                # Convert NaN to empty string, strip whitespace
                if pd.isna(value):
                    cleaned_row[key] = ''
                else:
                    cleaned_row[key] = str(value).strip()
            cleaned_data.append(cleaned_row)
        
        logger.info(f"Processed {len(cleaned_data)} rows of data")
        return cleaned_data
    
    def validate_sheet_structure(self, data: List[Dict]) -> bool:
        """
        Validate that the sheet has the expected structure for virtual events.
        
        Args:
            data (List[Dict]): Sheet data to validate
            
        Returns:
            bool: True if structure is valid, False otherwise
        """
        if not data:
            logger.error("No data to validate")
            return False
        
        # Check for required columns
        required_columns = [
            'Status', 'Date', 'Time', 'Session Type', 'Teacher Name',
            'School Name', 'School Level', 'District', 'Session Title',
            'Presenter', 'Organization', 'Presenter Location', 'Topic/Theme',
            'Session Link'
        ]
        
        first_row = data[0]
        missing_columns = []
        
        for column in required_columns:
            if column not in first_row:
                missing_columns.append(column)
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        logger.info("Sheet structure validation passed")
        return True
    
    def get_sheet_info(self, sheet_id: str) -> Dict:
        """
        Get basic information about the sheet.
        
        Args:
            sheet_id (str): Google Sheet ID
            
        Returns:
            Dict: Sheet information including row count, column count, etc.
        """
        try:
            data = self.read_sheet_data(sheet_id)
            
            if not data:
                return {
                    'sheet_id': sheet_id,
                    'row_count': 0,
                    'column_count': 0,
                    'valid_structure': False,
                    'error': 'No data found'
                }
            
            # Get column information
            columns = list(data[0].keys()) if data else []
            
            # Count rows with actual data (non-empty Session Link)
            data_rows = 0
            for row in data:
                if row.get('Session Link', '').strip():
                    data_rows += 1
            
            return {
                'sheet_id': sheet_id,
                'row_count': len(data),
                'data_rows': data_rows,
                'column_count': len(columns),
                'columns': columns,
                'valid_structure': self.validate_sheet_structure(data),
                'sample_row': data[0] if data else None
            }
            
        except Exception as e:
            logger.error(f"Error getting sheet info: {str(e)}")
            return {
                'sheet_id': sheet_id,
                'error': str(e),
                'valid_structure': False
            }

def test_google_sheets_service():
    """Test function for the Google Sheets service"""
    service = GoogleSheetsService()
    
    # Test with a sample sheet ID (you would replace this with a real one)
    test_sheet_id = "test_sheet_id_here"
    
    try:
        print("Testing Google Sheets Service...")
        
        # Test sheet info
        info = service.get_sheet_info(test_sheet_id)
        print(f"Sheet Info: {info}")
        
        # Test data reading
        data = service.read_sheet_data(test_sheet_id)
        print(f"Read {len(data)} rows of data")
        
        if data:
            print("Sample row:")
            print(data[0])
        
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_google_sheets_service()
