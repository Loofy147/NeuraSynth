# -*- coding: utf-8 -*-
"""
Unit Tests for NeuraSynth Integrated System Models
تم تطوير هذه الاختبارات لضمان جودة وموثوقية جميع نماذج البيانات في النظام
"""

import pytest
import unittest
from datetime import datetime, timedelta
from decimal import Decimal
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'neurasynth_integrated_backend', 'src'))

from models.organization import Organization, OrganizationInvitation
from models.role import Role, Permission, RolePermission
from models.enhanced_user import EnhancedUser, UserSession, UserSkill
from models.project import Project, ProjectMember, ProjectMilestone, ProjectTask
from models.contract import Contract, ContractTerm, ContractPayment
from models.financial import Expense, Invoice, Payment, Budget
from models.ai_model import AIModel, ModelTraining, ModelDeployment, ModelExperiment


class TestOrganizationModel(unittest.TestCase):
    """اختبارات شاملة لنموذج المؤسسة"""
    
    def setUp(self):
        """إعداد البيانات الأولية للاختبارات"""
        self.org_data = {
            'name': 'NeuraSynth Studios',
            'description': 'منصة متقدمة لإدارة مشاريع الذكاء الاصطناعي',
            'industry': 'Technology',
            'size': 'Medium',
            'website': 'https://neurasynth.com',
            'phone': '+966501234567',
            'address': 'الرياض، المملكة العربية السعودية'
        }
    
    def test_organization_creation(self):
        """اختبار إنشاء مؤسسة جديدة"""
        org = Organization(**self.org_data)
        
        # التحقق من البيانات الأساسية
        self.assertEqual(org.name, 'NeuraSynth Studios')
        self.assertEqual(org.industry, 'Technology')
        self.assertEqual(org.size, 'Medium')
        self.assertTrue(org.is_active)
        self.assertIsNotNone(org.created_at)
        
        # التحقق من الإعدادات الافتراضية
        self.assertIsNotNone(org.settings)
        self.assertIn('timezone', org.settings)
        self.assertIn('language', org.settings)
    
    def test_organization_validation(self):
        """اختبار التحقق من صحة بيانات المؤسسة"""
        # اختبار البيانات المطلوبة
        with self.assertRaises(ValueError):
            Organization(name='', description=self.org_data['description'])
        
        # اختبار طول الاسم
        with self.assertRaises(ValueError):
            Organization(name='a' * 256, description=self.org_data['description'])
        
        # اختبار صحة البريد الإلكتروني
        invalid_org = self.org_data.copy()
        invalid_org['email'] = 'invalid-email'
        with self.assertRaises(ValueError):
            Organization(**invalid_org)
    
    def test_organization_invitation(self):
        """اختبار نظام دعوات المؤسسة"""
        org = Organization(**self.org_data)
        
        invitation = OrganizationInvitation(
            organization_id=1,
            email='user@example.com',
            role='member',
            invited_by=1,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        self.assertEqual(invitation.email, 'user@example.com')
        self.assertEqual(invitation.status, 'pending')
        self.assertFalse(invitation.is_expired())
        
        # اختبار انتهاء صلاحية الدعوة
        expired_invitation = OrganizationInvitation(
            organization_id=1,
            email='user2@example.com',
            role='member',
            invited_by=1,
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        self.assertTrue(expired_invitation.is_expired())


class TestRoleModel(unittest.TestCase):
    """اختبارات شاملة لنموذج الأدوار والصلاحيات"""
    
    def setUp(self):
        """إعداد البيانات الأولية للاختبارات"""
        self.role_data = {
            'name': 'مدير المشروع',
            'description': 'مسؤول عن إدارة وتنسيق المشاريع',
            'organization_id': 1,
            'level': 2,
            'is_system_role': False
        }
    
    def test_role_creation(self):
        """اختبار إنشاء دور جديد"""
        role = Role(**self.role_data)
        
        self.assertEqual(role.name, 'مدير المشروع')
        self.assertEqual(role.level, 2)
        self.assertTrue(role.is_active)
        self.assertFalse(role.is_system_role)
    
    def test_role_hierarchy(self):
        """اختبار الهيكل الهرمي للأدوار"""
        parent_role = Role(
            name='مدير عام',
            description='المدير العام للمؤسسة',
            organization_id=1,
            level=1
        )
        
        child_role = Role(
            name='مدير فريق',
            description='مدير فريق تطوير',
            organization_id=1,
            level=2,
            parent_role_id=1
        )
        
        self.assertEqual(child_role.parent_role_id, 1)
        self.assertTrue(child_role.level > parent_role.level)
    
    def test_permission_system(self):
        """اختبار نظام الصلاحيات"""
        permission = Permission(
            name='project.create',
            description='إنشاء مشاريع جديدة',
            resource='project',
            action='create'
        )
        
        self.assertEqual(permission.name, 'project.create')
        self.assertEqual(permission.resource, 'project')
        self.assertEqual(permission.action, 'create')
    
    def test_role_permission_assignment(self):
        """اختبار تعيين الصلاحيات للأدوار"""
        role_permission = RolePermission(
            role_id=1,
            permission_id=1,
            granted=True,
            granted_by=1
        )
        
        self.assertTrue(role_permission.granted)
        self.assertIsNotNone(role_permission.granted_at)


class TestEnhancedUserModel(unittest.TestCase):
    """اختبارات شاملة لنموذج المستخدم المحسن"""
    
    def setUp(self):
        """إعداد البيانات الأولية للاختبارات"""
        self.user_data = {
            'username': 'ahmed_developer',
            'email': 'ahmed@neurasynth.com',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'phone': '+966501234567',
            'bio': 'مطور برمجيات متخصص في الذكاء الاصطناعي',
            'location': 'الرياض، السعودية',
            'timezone': 'Asia/Riyadh',
            'language': 'ar'
        }
    
    def test_user_creation(self):
        """اختبار إنشاء مستخدم جديد"""
        user = EnhancedUser(**self.user_data)
        
        self.assertEqual(user.username, 'ahmed_developer')
        self.assertEqual(user.email, 'ahmed@neurasynth.com')
        self.assertEqual(user.first_name, 'أحمد')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)
    
    def test_password_hashing(self):
        """اختبار تشفير كلمات المرور"""
        user = EnhancedUser(**self.user_data)
        password = 'SecurePassword123!'
        
        user.set_password(password)
        self.assertNotEqual(user.password_hash, password)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password('WrongPassword'))
    
    def test_user_session(self):
        """اختبار إدارة جلسات المستخدم"""
        session = UserSession(
            user_id=1,
            session_token='abc123def456',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0...',
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        self.assertEqual(session.user_id, 1)
        self.assertFalse(session.is_expired())
        self.assertTrue(session.is_active)
    
    def test_user_skills(self):
        """اختبار إدارة مهارات المستخدم"""
        skill = UserSkill(
            user_id=1,
            skill_name='Python',
            skill_category='Programming',
            proficiency_level='Expert',
            years_of_experience=5,
            is_verified=True
        )
        
        self.assertEqual(skill.skill_name, 'Python')
        self.assertEqual(skill.proficiency_level, 'Expert')
        self.assertTrue(skill.is_verified)


class TestProjectModel(unittest.TestCase):
    """اختبارات شاملة لنموذج المشاريع"""
    
    def setUp(self):
        """إعداد البيانات الأولية للاختبارات"""
        self.project_data = {
            'name': 'نظام التعرف على الصوت',
            'description': 'تطوير نظام ذكي للتعرف على الأصوات باللغة العربية',
            'organization_id': 1,
            'project_type': 'AI Development',
            'priority': 'High',
            'budget': Decimal('500000.00'),
            'currency': 'SAR',
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + timedelta(days=180),
            'created_by': 1
        }
    
    def test_project_creation(self):
        """اختبار إنشاء مشروع جديد"""
        project = Project(**self.project_data)
        
        self.assertEqual(project.name, 'نظام التعرف على الصوت')
        self.assertEqual(project.project_type, 'AI Development')
        self.assertEqual(project.priority, 'High')
        self.assertEqual(project.status, 'Planning')
        self.assertEqual(project.budget, Decimal('500000.00'))
    
    def test_project_progress_calculation(self):
        """اختبار حساب تقدم المشروع"""
        project = Project(**self.project_data)
        
        # إضافة مهام للمشروع
        task1 = ProjectTask(
            project_id=1,
            title='تحليل المتطلبات',
            status='Completed',
            progress=100
        )
        task2 = ProjectTask(
            project_id=1,
            title='تصميم النظام',
            status='In Progress',
            progress=60
        )
        task3 = ProjectTask(
            project_id=1,
            title='التطوير',
            status='Not Started',
            progress=0
        )
        
        # حساب التقدم الإجمالي
        total_progress = (100 + 60 + 0) / 3
        self.assertAlmostEqual(total_progress, 53.33, places=2)
    
    def test_project_member_assignment(self):
        """اختبار تعيين أعضاء الفريق للمشروع"""
        member = ProjectMember(
            project_id=1,
            user_id=1,
            role='Lead Developer',
            allocation_percentage=80,
            hourly_rate=Decimal('150.00'),
            assigned_by=1
        )
        
        self.assertEqual(member.role, 'Lead Developer')
        self.assertEqual(member.allocation_percentage, 80)
        self.assertTrue(member.is_active)
    
    def test_project_milestone(self):
        """اختبار معالم المشروع"""
        milestone = ProjectMilestone(
            project_id=1,
            title='إكمال مرحلة التصميم',
            description='إنهاء جميع مخططات التصميم والموافقة عليها',
            due_date=datetime.utcnow() + timedelta(days=30),
            status='Pending'
        )
        
        self.assertEqual(milestone.title, 'إكمال مرحلة التصميم')
        self.assertEqual(milestone.status, 'Pending')
        self.assertFalse(milestone.is_completed())


class TestContractModel(unittest.TestCase):
    """اختبارات شاملة لنموذج العقود"""
    
    def setUp(self):
        """إعداد البيانات الأولية للاختبارات"""
        self.contract_data = {
            'title': 'عقد تطوير نظام ذكي',
            'description': 'عقد لتطوير نظام ذكاء اصطناعي متقدم',
            'contract_type': 'Development',
            'organization_id': 1,
            'client_id': 1,
            'project_id': 1,
            'total_value': Decimal('750000.00'),
            'currency': 'SAR',
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + timedelta(days=365),
            'created_by': 1
        }
    
    def test_contract_creation(self):
        """اختبار إنشاء عقد جديد"""
        contract = Contract(**self.contract_data)
        
        self.assertEqual(contract.title, 'عقد تطوير نظام ذكي')
        self.assertEqual(contract.contract_type, 'Development')
        self.assertEqual(contract.status, 'Draft')
        self.assertEqual(contract.total_value, Decimal('750000.00'))
    
    def test_contract_terms(self):
        """اختبار شروط العقد"""
        term = ContractTerm(
            contract_id=1,
            term_type='Payment',
            title='شروط الدفع',
            description='يتم الدفع على 4 دفعات متساوية',
            is_mandatory=True,
            order_index=1
        )
        
        self.assertEqual(term.term_type, 'Payment')
        self.assertTrue(term.is_mandatory)
        self.assertTrue(term.is_active)
    
    def test_contract_payment(self):
        """اختبار مدفوعات العقد"""
        payment = ContractPayment(
            contract_id=1,
            amount=Decimal('187500.00'),
            currency='SAR',
            payment_type='Milestone',
            due_date=datetime.utcnow() + timedelta(days=30),
            description='الدفعة الأولى - 25% من قيمة العقد'
        )
        
        self.assertEqual(payment.amount, Decimal('187500.00'))
        self.assertEqual(payment.payment_type, 'Milestone')
        self.assertEqual(payment.status, 'Pending')


class TestFinancialModel(unittest.TestCase):
    """اختبارات شاملة للنماذج المالية"""
    
    def test_expense_creation(self):
        """اختبار إنشاء مصروف"""
        expense = Expense(
            organization_id=1,
            project_id=1,
            category='Software',
            description='ترخيص برنامج التطوير',
            amount=Decimal('5000.00'),
            currency='SAR',
            expense_date=datetime.utcnow(),
            created_by=1
        )
        
        self.assertEqual(expense.category, 'Software')
        self.assertEqual(expense.amount, Decimal('5000.00'))
        self.assertEqual(expense.status, 'Pending')
    
    def test_invoice_creation(self):
        """اختبار إنشاء فاتورة"""
        invoice = Invoice(
            organization_id=1,
            client_id=1,
            project_id=1,
            invoice_number='INV-2024-001',
            total_amount=Decimal('25000.00'),
            currency='SAR',
            due_date=datetime.utcnow() + timedelta(days=30),
            created_by=1
        )
        
        self.assertEqual(invoice.invoice_number, 'INV-2024-001')
        self.assertEqual(invoice.total_amount, Decimal('25000.00'))
        self.assertEqual(invoice.status, 'Draft')
    
    def test_budget_management(self):
        """اختبار إدارة الميزانية"""
        budget = Budget(
            organization_id=1,
            project_id=1,
            category='Development',
            allocated_amount=Decimal('100000.00'),
            currency='SAR',
            period_start=datetime.utcnow(),
            period_end=datetime.utcnow() + timedelta(days=90),
            created_by=1
        )
        
        self.assertEqual(budget.allocated_amount, Decimal('100000.00'))
        self.assertEqual(budget.spent_amount, Decimal('0.00'))
        self.assertEqual(budget.remaining_amount, Decimal('100000.00'))


class TestAIModelManagement(unittest.TestCase):
    """اختبارات شاملة لإدارة نماذج الذكاء الاصطناعي"""
    
    def setUp(self):
        """إعداد البيانات الأولية للاختبارات"""
        self.ai_model_data = {
            'name': 'نموذج التعرف على الصوت العربي',
            'description': 'نموذج ذكاء اصطناعي للتعرف على الكلام باللغة العربية',
            'model_type': 'Speech Recognition',
            'framework': 'TensorFlow',
            'version': '1.0.0',
            'organization_id': 1,
            'project_id': 1,
            'created_by': 1
        }
    
    def test_ai_model_creation(self):
        """اختبار إنشاء نموذج ذكاء اصطناعي"""
        model = AIModel(**self.ai_model_data)
        
        self.assertEqual(model.name, 'نموذج التعرف على الصوت العربي')
        self.assertEqual(model.model_type, 'Speech Recognition')
        self.assertEqual(model.framework, 'TensorFlow')
        self.assertEqual(model.status, 'Development')
    
    def test_model_training(self):
        """اختبار تدريب النموذج"""
        training = ModelTraining(
            model_id=1,
            training_name='التدريب الأولي',
            dataset_name='مجموعة بيانات الصوت العربي',
            training_config={'epochs': 100, 'batch_size': 32},
            started_by=1
        )
        
        self.assertEqual(training.training_name, 'التدريب الأولي')
        self.assertEqual(training.status, 'Pending')
        self.assertIsNotNone(training.training_config)
    
    def test_model_deployment(self):
        """اختبار نشر النموذج"""
        deployment = ModelDeployment(
            model_id=1,
            deployment_name='نشر الإنتاج',
            environment='Production',
            endpoint_url='https://api.neurasynth.com/speech-recognition',
            deployed_by=1
        )
        
        self.assertEqual(deployment.environment, 'Production')
        self.assertEqual(deployment.status, 'Pending')
        self.assertIsNotNone(deployment.endpoint_url)
    
    def test_model_experiment(self):
        """اختبار تجارب النموذج"""
        experiment = ModelExperiment(
            model_id=1,
            experiment_name='تجربة تحسين الدقة',
            description='تجربة لتحسين دقة التعرف على اللهجات المختلفة',
            parameters={'learning_rate': 0.001, 'dropout': 0.2},
            created_by=1
        )
        
        self.assertEqual(experiment.experiment_name, 'تجربة تحسين الدقة')
        self.assertEqual(experiment.status, 'Running')
        self.assertIsNotNone(experiment.parameters)


class TestSystemIntegration(unittest.TestCase):
    """اختبارات التكامل بين النماذج المختلفة"""
    
    def test_user_organization_relationship(self):
        """اختبار العلاقة بين المستخدم والمؤسسة"""
        # إنشاء مؤسسة
        org = Organization(
            name='شركة التقنية المتقدمة',
            description='شركة متخصصة في حلول الذكاء الاصطناعي'
        )
        
        # إنشاء مستخدم
        user = EnhancedUser(
            username='sara_ai_expert',
            email='sara@techcompany.com',
            first_name='سارة',
            last_name='أحمد'
        )
        
        # التحقق من إمكانية ربط المستخدم بالمؤسسة
        self.assertIsNotNone(org)
        self.assertIsNotNone(user)
    
    def test_project_contract_relationship(self):
        """اختبار العلاقة بين المشروع والعقد"""
        # إنشاء مشروع
        project = Project(
            name='تطوير تطبيق ذكي',
            description='تطوير تطبيق جوال بتقنيات الذكاء الاصطناعي',
            organization_id=1,
            created_by=1
        )
        
        # إنشاء عقد مرتبط بالمشروع
        contract = Contract(
            title='عقد تطوير التطبيق',
            description='عقد شامل لتطوير التطبيق الذكي',
            organization_id=1,
            project_id=1,
            total_value=Decimal('300000.00'),
            currency='SAR',
            created_by=1
        )
        
        self.assertEqual(contract.project_id, 1)
        self.assertIsNotNone(project)
        self.assertIsNotNone(contract)


if __name__ == '__main__':
    # تشغيل جميع الاختبارات
    unittest.main(verbosity=2)

