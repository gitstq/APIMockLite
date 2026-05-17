"""
AI-Powered Response Generator for APIMockLite

This module provides intelligent response generation capabilities
without requiring external AI services - using rule-based generation
with realistic data patterns.
"""

import json
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class ResponseGenerator:
    """Generate realistic mock responses based on endpoint patterns"""
    
    # Common data patterns for realistic generation
    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
        "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
    ]
    
    DOMAINS = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
        "company.com", "enterprise.io", "tech.dev", "startup.co"
    ]
    
    COMPANIES = [
        "TechCorp", "InnovateLab", "DataSystems", "CloudNine", "ByteWorks",
        "CodeCraft", "DevStudio", "AppForge", "NetSolutions", "DigitalPeak"
    ]
    
    PRODUCTS = [
        "Pro", "Enterprise", "Lite", "Standard", "Premium", "Basic", "Ultimate"
    ]
    
    STATUSES = ["active", "inactive", "pending", "suspended", "archived"]
    
    CATEGORIES = [
        "electronics", "clothing", "food", "books", "software", "services",
        "hardware", "furniture", "accessories", "tools"
    ]
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize generator with optional seed for reproducibility"""
        if seed is not None:
            random.seed(seed)
    
    def generate_id(self, prefix: str = "id") -> str:
        """Generate a unique ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{prefix}_{timestamp}_{random_suffix}"
    
    def generate_uuid(self) -> str:
        """Generate a UUID-like string"""
        parts = []
        for length in [8, 4, 4, 4, 12]:
            parts.append(''.join(random.choices(string.hexdigits.lower(), k=length)))
        return '-'.join(parts)
    
    def generate_name(self) -> str:
        """Generate a random full name"""
        return f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}"
    
    def generate_email(self, name: Optional[str] = None) -> str:
        """Generate a random email address"""
        if name is None:
            name = self.generate_name().lower().replace(" ", ".")
        else:
            name = name.lower().replace(" ", ".")
        domain = random.choice(self.DOMAINS)
        return f"{name}@{domain}"
    
    def generate_phone(self) -> str:
        """Generate a random phone number"""
        return f"+1 ({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    def generate_address(self) -> Dict[str, str]:
        """Generate a random address"""
        street_num = random.randint(100, 9999)
        streets = ["Main St", "Oak Ave", "Park Rd", "Elm St", "Maple Dr", "Cedar Ln"]
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
        states = ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA"]
        
        return {
            "street": f"{street_num} {random.choice(streets)}",
            "city": random.choice(cities),
            "state": random.choice(states),
            "zip": f"{random.randint(10000, 99999)}",
            "country": "USA"
        }
    
    def generate_date(self, days_range: int = 365) -> str:
        """Generate a random date within the specified range"""
        days_ago = random.randint(0, days_range)
        date = datetime.now() - timedelta(days=days_ago)
        return date.isoformat()
    
    def generate_timestamp(self) -> int:
        """Generate a Unix timestamp"""
        return int(datetime.now().timestamp())
    
    def generate_company(self) -> str:
        """Generate a random company name"""
        return random.choice(self.COMPANIES)
    
    def generate_product(self) -> Dict[str, Any]:
        """Generate a random product"""
        product_id = self.generate_id("prod")
        name = f"{random.choice(self.COMPANIES)} {random.choice(self.PRODUCTS)}"
        
        return {
            "id": product_id,
            "name": name,
            "description": f"High-quality {name.lower()} product for professional use",
            "price": round(random.uniform(9.99, 999.99), 2),
            "category": random.choice(self.CATEGORIES),
            "status": random.choice(self.STATUSES),
            "stock": random.randint(0, 1000),
            "sku": f"SKU-{random.randint(10000, 99999)}",
            "created_at": self.generate_date()
        }
    
    def generate_user(self) -> Dict[str, Any]:
        """Generate a random user"""
        name = self.generate_name()
        user_id = self.generate_id("user")
        
        return {
            "id": user_id,
            "name": name,
            "email": self.generate_email(name),
            "phone": self.generate_phone(),
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_id}",
            "role": random.choice(["admin", "user", "editor", "viewer"]),
            "status": random.choice(self.STATUSES),
            "created_at": self.generate_date(),
            "last_login": self.generate_date(30),
            "address": self.generate_address()
        }
    
    def generate_order(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate a random order"""
        if user_id is None:
            user_id = self.generate_id("user")
        
        num_items = random.randint(1, 5)
        items = [self.generate_product() for _ in range(num_items)]
        total = sum(item["price"] for item in items)
        
        return {
            "id": self.generate_id("order"),
            "user_id": user_id,
            "items": items,
            "total": round(total, 2),
            "status": random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
            "shipping_address": self.generate_address(),
            "created_at": self.generate_date(),
            "updated_at": self.generate_date(7)
        }
    
    def generate_list(self, item_generator, count: int = 10) -> List[Any]:
        """Generate a list of items"""
        return [item_generator() for _ in range(count)]
    
    def generate_paginated_response(
        self,
        items: List[Any],
        page: int = 1,
        per_page: int = 10,
        total: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a paginated response structure"""
        if total is None:
            total = len(items)
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated_items = items[start:end]
        
        return {
            "data": paginated_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
                "has_next": end < total,
                "has_prev": page > 1
            }
        }
    
    def generate_api_response(
        self,
        endpoint: str,
        method: str = "GET",
        data_type: Optional[str] = None
    ) -> Any:
        """Generate a response based on endpoint pattern"""
        endpoint_lower = endpoint.lower()
        
        # Determine data type from endpoint pattern
        if data_type is None:
            if any(word in endpoint_lower for word in ["user", "account", "profile", "auth"]):
                data_type = "user"
            elif any(word in endpoint_lower for word in ["product", "item", "goods"]):
                data_type = "product"
            elif any(word in endpoint_lower for word in ["order", "purchase", "transaction"]):
                data_type = "order"
            elif any(word in endpoint_lower for word in ["company", "organization", "business"]):
                data_type = "company"
            else:
                data_type = "generic"
        
        # Generate based on HTTP method
        if method.upper() == "GET":
            if "/" in endpoint and not endpoint.endswith("/"):
                # Likely a single item request
                if data_type == "user":
                    return {"data": self.generate_user()}
                elif data_type == "product":
                    return {"data": self.generate_product()}
                elif data_type == "order":
                    return {"data": self.generate_order()}
            else:
                # Likely a list request
                if data_type == "user":
                    items = self.generate_list(self.generate_user, random.randint(5, 20))
                elif data_type == "product":
                    items = self.generate_list(self.generate_product, random.randint(10, 50))
                elif data_type == "order":
                    items = self.generate_list(self.generate_order, random.randint(5, 30))
                else:
                    items = [{"id": self.generate_id(), "name": f"Item {i}"} for i in range(random.randint(5, 20))]
                
                return self.generate_paginated_response(items)
        
        elif method.upper() in ["POST", "PUT", "PATCH"]:
            # Return created/updated resource
            if data_type == "user":
                resource = self.generate_user()
            elif data_type == "product":
                resource = self.generate_product()
            elif data_type == "order":
                resource = self.generate_order()
            else:
                resource = {"id": self.generate_id(), "created": True}
            
            return {
                "data": resource,
                "message": f"Resource {method.lower()}ed successfully",
                "timestamp": self.generate_timestamp()
            }
        
        elif method.upper() == "DELETE":
            return {
                "message": "Resource deleted successfully",
                "deleted_at": self.generate_timestamp()
            }
        
        return {"message": "Success", "timestamp": self.generate_timestamp()}
    
    def generate_error_response(
        self,
        status_code: int = 400,
        message: Optional[str] = None,
        error_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an error response"""
        error_messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            422: "Unprocessable Entity",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }
        
        if message is None:
            message = error_messages.get(status_code, "Unknown Error")
        
        if error_type is None:
            error_type = message.lower().replace(" ", "_")
        
        return {
            "error": {
                "type": error_type,
                "message": message,
                "code": status_code,
                "timestamp": self.generate_timestamp(),
                "request_id": self.generate_uuid()
            }
        }