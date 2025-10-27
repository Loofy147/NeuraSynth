# -*- coding: utf-8 -*-
"""
Integration Tests for NeuraSynth Integrated System API Endpoints
اختبارات التكامل الشاملة لواجهات برمجة التطبيقات في النظام المتكامل
"""

import pytest
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal
import time


class TestAPIIntegration:
    """اختبارات التكامل لواجهات برمجة التطبيقات"""
    
    BASE_URL = "http://localhost:5000/api/v1"
    
    @classmethod
    def setup_class(cls):
        """إعداد البيانات الأولية للاختبارات"""
        cls.test_user = {
            "username": "test_user",
            "email": "test@neurasynth.com",
            "password": "TestPassword123!",
            "first_name": "مستخدم",
            "last_name": "تجريبي"
        }
        cls.auth_token = None
        cls.test_organization_id = None
        cls.test_project_id = None
    
    def test_01_user_registration(self):
        """اختبار تسجيل مستخدم جديد"""
        response = requests.post(
            f"{self.BASE_URL}/auth/register",
            json=self.test_user
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data
        assert data["message"] == "تم إنشاء الحساب بنجاح"
    
    def test_02_user_login(self):
        """اختبار تسجيل الدخول"""
        login_data = {
            "email": self.test_user["email"],
            "password": self.test_user["password"]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/auth/login",
            json=login_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        
        # حفظ رمز المصادقة للاختبارات التالية
        TestAPIIntegration.auth_token = data["access_token"]
    
    def test_03_create_organization(self):
        """اختبار إنشاء مؤسسة جديدة"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        org_data = {
            "name": "شركة الاختبار التقنية",
            "description": "شركة تجريبية لاختبار النظام",
            "industry": "Technology",
            "size": "Small"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/organizations",
            json=org_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "organization_id" in data
        TestAPIIntegration.test_organization_id = data["organization_id"]
    
    def test_04_create_project(self):
        """اختبار إنشاء مشروع جديد"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        project_data = {
            "name": "مشروع اختبار النظام",
            "description": "مشروع تجريبي لاختبار وظائف النظام",
            "project_type": "AI Development",
            "priority": "Medium",
            "budget": "100000.00",
            "currency": "SAR",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=90)).isoformat()
        }
        
        response = requests.post(
            f"{self.BASE_URL}/projects",
            json=project_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "project_id" in data
        TestAPIIntegration.test_project_id = data["project_id"]
    
    def test_05_get_projects(self):
        """اختبار استرجاع قائمة المشاريع"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        response = requests.get(
            f"{self.BASE_URL}/projects",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert len(data["projects"]) > 0
    
    def test_06_update_project(self):
        """اختبار تحديث مشروع"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        update_data = {
            "status": "In Progress",
            "progress": 25
        }
        
        response = requests.put(
            f"{self.BASE_URL}/projects/{self.test_project_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "In Progress"
        assert data["progress"] == 25
    
    def test_07_create_project_task(self):
        """اختبار إنشاء مهمة في المشروع"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        task_data = {
            "title": "مهمة اختبار",
            "description": "مهمة تجريبية لاختبار النظام",
            "priority": "High",
            "estimated_hours": 40,
            "due_date": (datetime.utcnow() + timedelta(days=14)).isoformat()
        }
        
        response = requests.post(
            f"{self.BASE_URL}/projects/{self.test_project_id}/tasks",
            json=task_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "task_id" in data
    
    def test_08_ai_project_matching(self):
        """اختبار نظام المطابقة الذكي للمشاريع"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        response = requests.get(
            f"{self.BASE_URL}/ai/project-matching/recommendations",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
    
    def test_09_create_contract(self):
        """اختبار إنشاء عقد"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        contract_data = {
            "title": "عقد اختبار",
            "description": "عقد تجريبي لاختبار النظام",
            "contract_type": "Development",
            "project_id": self.test_project_id,
            "total_value": "75000.00",
            "currency": "SAR",
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=180)).isoformat()
        }
        
        response = requests.post(
            f"{self.BASE_URL}/contracts",
            json=contract_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "contract_id" in data
    
    def test_10_financial_expense_tracking(self):
        """اختبار تتبع المصروفات المالية"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        expense_data = {
            "category": "Software",
            "description": "ترخيص برنامج تطوير",
            "amount": "2500.00",
            "currency": "SAR",
            "project_id": self.test_project_id
        }
        
        response = requests.post(
            f"{self.BASE_URL}/financial/expenses",
            json=expense_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "expense_id" in data
    
    def test_11_ai_model_management(self):
        """اختبار إدارة نماذج الذكاء الاصطناعي"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        model_data = {
            "name": "نموذج اختبار",
            "description": "نموذج تجريبي للاختبار",
            "model_type": "Classification",
            "framework": "TensorFlow",
            "version": "1.0.0",
            "project_id": self.test_project_id
        }
        
        response = requests.post(
            f"{self.BASE_URL}/ai/models",
            json=model_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "model_id" in data
    
    def test_12_system_analytics(self):
        """اختبار تحليلات النظام"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        response = requests.get(
            f"{self.BASE_URL}/analytics/dashboard",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "active_users" in data
        assert "revenue" in data
    
    def test_13_user_logout(self):
        """اختبار تسجيل الخروج"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        response = requests.post(
            f"{self.BASE_URL}/auth/logout",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "تم تسجيل الخروج بنجاح"


class TestAPIErrorHandling:
    """اختبارات معالجة الأخطاء في واجهات برمجة التطبيقات"""
    
    BASE_URL = "http://localhost:5000/api/v1"
    
    def test_invalid_authentication(self):
        """اختبار المصادقة غير الصحيحة"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = requests.get(
            f"{self.BASE_URL}/projects",
            headers=headers
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "error" in data
    
    def test_missing_required_fields(self):
        """اختبار الحقول المطلوبة المفقودة"""
        incomplete_data = {
            "name": "مشروع ناقص"
            # missing required fields
        }
        
        response = requests.post(
            f"{self.BASE_URL}/projects",
            json=incomplete_data
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "validation_errors" in data
    
    def test_resource_not_found(self):
        """اختبار المورد غير الموجود"""
        response = requests.get(f"{self.BASE_URL}/projects/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["error"] == "المشروع غير موجود"
    
    def test_rate_limiting(self):
        """اختبار تحديد معدل الطلبات"""
        # إرسال طلبات متعددة بسرعة
        for i in range(100):
            response = requests.get(f"{self.BASE_URL}/health")
            if response.status_code == 429:
                assert "rate_limit_exceeded" in response.json()
                break
            time.sleep(0.01)


class TestAPIPerformance:
    """اختبارات الأداء لواجهات برمجة التطبيقات"""
    
    BASE_URL = "http://localhost:5000/api/v1"
    
    def test_response_time(self):
        """اختبار زمن الاستجابة"""
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0  # يجب أن يكون زمن الاستجابة أقل من ثانية واحدة
        assert response.status_code == 200
    
    def test_concurrent_requests(self):
        """اختبار الطلبات المتزامنة"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = requests.get(f"{self.BASE_URL}/health", timeout=5)
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # إنشاء 50 طلب متزامن
        threads = []
        for i in range(50):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # انتظار انتهاء جميع الطلبات
        for thread in threads:
            thread.join()
        
        # التحقق من النتائج
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        # يجب أن تنجح معظم الطلبات
        assert success_count >= 45


if __name__ == '__main__':
    # تشغيل اختبارات التكامل
    pytest.main([__file__, '-v'])

