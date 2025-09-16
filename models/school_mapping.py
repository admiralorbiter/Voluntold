from models import db
from dataclasses import dataclass
import csv
from pathlib import Path

class SchoolMapping(db.Model):
    __tablename__ = 'school_mappings'

    """Provides a model for mapping PrepKC's associated schools with info and their ID's"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(255), nullable=False)
    parent_salesforce_id = db.Column(db.String(255), nullable=False)
    
    @classmethod
    def load_from_csv(cls, filepath: str | Path) -> list['SchoolMapping']:
        """Load school mappings from CSV file"""
        mappings = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mapping = cls(
                    name=row['Name'],
                    district=row['District'],
                    parent_salesforce_id=row['Parent_Salesforce_ID']
                )
                mappings.append(mapping)
        return mappings
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'district': self.district,
            'parent_salesforce_id': self.parent_salesforce_id
        }

    @staticmethod
    def save_to_csv(mappings: list['SchoolMapping'], filepath: str | Path) -> None:
        """Save school mappings to CSV file"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Name', 'District', 'Parent_Salesforce_ID'])
            writer.writeheader()
            for mapping in mappings:
                writer.writerow({
                    'Name': mapping.name,
                    'District': mapping.district,
                    'Parent_Salesforce_ID': mapping.parent_salesforce_id
                }) 