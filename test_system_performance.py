# -*- coding: utf-8 -*-
"""
Performance Tests for NeuraSynth Integrated System
اختبارات الأداء الشاملة للنظام المتكامل
"""

import time
import threading
import psutil
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json


class SystemPerformanceTests:
    """اختبارات الأداء الشاملة للنظام"""
    
    def __init__(self):
        self.base_url = "http://localhost:5000/api/v1"
        self.frontend_url = "http://localhost:5173"
        self.results = {}
    
    def test_memory_usage(self):
        """اختبار استخدام الذاكرة"""
        print("🧠 اختبار استخدام الذاكرة...")
        
        # قياس استخدام الذاكرة قبل التحميل
        initial_memory = psutil.virtual_memory().percent
        
        # محاكاة تحميل النظام
        self._simulate_system_load()
        
        # قياس استخدام الذاكرة بعد التحميل
        peak_memory = psutil.virtual_memory().percent
        
        memory_increase = peak_memory - initial_memory
        
        self.results['memory_usage'] = {
            'initial_memory_percent': initial_memory,
            'peak_memory_percent': peak_memory,
            'memory_increase_percent': memory_increase,
            'status': 'PASS' if memory_increase < 50 else 'FAIL'
        }
        
        print(f"   📊 الذاكرة الأولية: {initial_memory:.1f}%")
        print(f"   📈 ذروة الاستخدام: {peak_memory:.1f}%")
        print(f"   📋 الزيادة: {memory_increase:.1f}%")
        print(f"   ✅ النتيجة: {'نجح' if memory_increase < 50 else 'فشل'}")
    
    def test_cpu_usage(self):
        """اختبار استخدام المعالج"""
        print("\n🖥️ اختبار استخدام المعالج...")
        
        # مراقبة استخدام المعالج لمدة 30 ثانية
        cpu_readings = []
        for i in range(30):
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_readings.append(cpu_percent)
        
        avg_cpu = statistics.mean(cpu_readings)
        max_cpu = max(cpu_readings)
        
        self.results['cpu_usage'] = {
            'average_cpu_percent': avg_cpu,
            'peak_cpu_percent': max_cpu,
            'readings': cpu_readings,
            'status': 'PASS' if avg_cpu < 80 else 'FAIL'
        }
        
        print(f"   📊 متوسط الاستخدام: {avg_cpu:.1f}%")
        print(f"   📈 ذروة الاستخدام: {max_cpu:.1f}%")
        print(f"   ✅ النتيجة: {'نجح' if avg_cpu < 80 else 'فشل'}")
    
    def test_api_response_times(self):
        """اختبار أزمنة استجابة واجهات برمجة التطبيقات"""
        print("\n⚡ اختبار أزمنة استجابة APIs...")
        
        endpoints = [
            '/health',
            '/auth/login',
            '/projects',
            '/organizations',
            '/ai/models'
        ]
        
        response_times = {}
        
        for endpoint in endpoints:
            times = []
            for i in range(10):  # 10 طلبات لكل endpoint
                start_time = time.time()
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # بالميلي ثانية
                    times.append(response_time)
                except Exception as e:
                    times.append(5000)  # 5 ثوان في حالة الخطأ
            
            avg_time = statistics.mean(times)
            response_times[endpoint] = {
                'average_ms': avg_time,
                'min_ms': min(times),
                'max_ms': max(times),
                'status': 'PASS' if avg_time < 1000 else 'FAIL'
            }
            
            print(f"   📍 {endpoint}: {avg_time:.0f}ms (متوسط)")
        
        self.results['api_response_times'] = response_times
    
    def test_concurrent_users(self):
        """اختبار المستخدمين المتزامنين"""
        print("\n👥 اختبار المستخدمين المتزامنين...")
        
        def simulate_user_session():
            """محاكاة جلسة مستخدم"""
            session_start = time.time()
            try:
                # تسجيل دخول
                login_response = requests.post(f"{self.base_url}/auth/login", 
                                             json={"email": "test@example.com", "password": "password"})
                
                # استعراض المشاريع
                projects_response = requests.get(f"{self.base_url}/projects")
                
                # إنشاء مشروع جديد
                create_response = requests.post(f"{self.base_url}/projects",
                                              json={"name": "Test Project", "description": "Test"})
                
                session_end = time.time()
                return {
                    'duration': session_end - session_start,
                    'success': True,
                    'requests_made': 3
                }
            except Exception as e:
                return {
                    'duration': time.time() - session_start,
                    'success': False,
                    'error': str(e)
                }
        
        # محاكاة 50 مستخدم متزامن
        concurrent_users = 50
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(simulate_user_session) for _ in range(concurrent_users)]
            results = [future.result() for future in as_completed(futures)]
        
        successful_sessions = [r for r in results if r['success']]
        failed_sessions = [r for r in results if not r['success']]
        
        if successful_sessions:
            avg_duration = statistics.mean([s['duration'] for s in successful_sessions])
        else:
            avg_duration = 0
        
        success_rate = len(successful_sessions) / len(results) * 100
        
        self.results['concurrent_users'] = {
            'total_users': concurrent_users,
            'successful_sessions': len(successful_sessions),
            'failed_sessions': len(failed_sessions),
            'success_rate_percent': success_rate,
            'average_session_duration': avg_duration,
            'status': 'PASS' if success_rate >= 90 else 'FAIL'
        }
        
        print(f"   👤 إجمالي المستخدمين: {concurrent_users}")
        print(f"   ✅ جلسات ناجحة: {len(successful_sessions)}")
        print(f"   ❌ جلسات فاشلة: {len(failed_sessions)}")
        print(f"   📊 معدل النجاح: {success_rate:.1f}%")
        print(f"   ⏱️ متوسط مدة الجلسة: {avg_duration:.2f}s")
    
    def test_database_performance(self):
        """اختبار أداء قاعدة البيانات"""
        print("\n🗄️ اختبار أداء قاعدة البيانات...")
        
        # اختبار عمليات القراءة
        read_times = []
        for i in range(100):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}/projects")
                end_time = time.time()
                read_times.append((end_time - start_time) * 1000)
            except:
                read_times.append(5000)
        
        # اختبار عمليات الكتابة
        write_times = []
        for i in range(50):
            start_time = time.time()
            try:
                response = requests.post(f"{self.base_url}/projects",
                                       json={"name": f"Test Project {i}", "description": "Performance test"})
                end_time = time.time()
                write_times.append((end_time - start_time) * 1000)
            except:
                write_times.append(5000)
        
        avg_read_time = statistics.mean(read_times)
        avg_write_time = statistics.mean(write_times)
        
        self.results['database_performance'] = {
            'average_read_time_ms': avg_read_time,
            'average_write_time_ms': avg_write_time,
            'read_operations': len(read_times),
            'write_operations': len(write_times),
            'status': 'PASS' if avg_read_time < 500 and avg_write_time < 1000 else 'FAIL'
        }
        
        print(f"   📖 متوسط وقت القراءة: {avg_read_time:.0f}ms")
        print(f"   ✍️ متوسط وقت الكتابة: {avg_write_time:.0f}ms")
        print(f"   ✅ النتيجة: {'نجح' if avg_read_time < 500 and avg_write_time < 1000 else 'فشل'}")
    
    def test_frontend_performance(self):
        """اختبار أداء الواجهة الأمامية"""
        print("\n🎨 اختبار أداء الواجهة الأمامية...")
        
        load_times = []
        for i in range(10):
            start_time = time.time()
            try:
                response = requests.get(self.frontend_url, timeout=10)
                end_time = time.time()
                load_time = (end_time - start_time) * 1000
                load_times.append(load_time)
            except:
                load_times.append(10000)
        
        avg_load_time = statistics.mean(load_times)
        
        self.results['frontend_performance'] = {
            'average_load_time_ms': avg_load_time,
            'min_load_time_ms': min(load_times),
            'max_load_time_ms': max(load_times),
            'status': 'PASS' if avg_load_time < 3000 else 'FAIL'
        }
        
        print(f"   ⏱️ متوسط وقت التحميل: {avg_load_time:.0f}ms")
        print(f"   ✅ النتيجة: {'نجح' if avg_load_time < 3000 else 'فشل'}")
    
    def test_ai_processing_performance(self):
        """اختبار أداء معالجة الذكاء الاصطناعي"""
        print("\n🤖 اختبار أداء معالجة الذكاء الاصطناعي...")
        
        # اختبار نظام المطابقة الذكي
        matching_times = []
        for i in range(20):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_url}/ai/project-matching/recommendations")
                end_time = time.time()
                matching_times.append((end_time - start_time) * 1000)
            except:
                matching_times.append(10000)
        
        avg_matching_time = statistics.mean(matching_times)
        
        self.results['ai_processing_performance'] = {
            'average_matching_time_ms': avg_matching_time,
            'min_matching_time_ms': min(matching_times),
            'max_matching_time_ms': max(matching_times),
            'status': 'PASS' if avg_matching_time < 2000 else 'FAIL'
        }
        
        print(f"   🎯 متوسط وقت المطابقة: {avg_matching_time:.0f}ms")
        print(f"   ✅ النتيجة: {'نجح' if avg_matching_time < 2000 else 'فشل'}")
    
    def _simulate_system_load(self):
        """محاكاة تحميل النظام"""
        def load_worker():
            for i in range(50):
                try:
                    requests.get(f"{self.base_url}/health", timeout=1)
                except:
                    pass
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=load_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
    
    def generate_performance_report(self):
        """إنشاء تقرير الأداء"""
        print("\n📊 تقرير الأداء الشامل")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get('status') == 'PASS')
        
        print(f"📈 إجمالي الاختبارات: {total_tests}")
        print(f"✅ اختبارات ناجحة: {passed_tests}")
        print(f"❌ اختبارات فاشلة: {total_tests - passed_tests}")
        print(f"📊 معدل النجاح: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 تفاصيل النتائج:")
        for test_name, result in self.results.items():
            status_icon = "✅" if result.get('status') == 'PASS' else "❌"
            print(f"   {status_icon} {test_name}: {result.get('status', 'UNKNOWN')}")
        
        # حفظ التقرير في ملف
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'success_rate': (passed_tests/total_tests)*100
            },
            'detailed_results': self.results
        }
        
        with open('/home/ubuntu/NeuraSynth_Integrated_System/tests/performance/performance_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير المفصل في: performance_report.json")
    
    def run_all_tests(self):
        """تشغيل جميع اختبارات الأداء"""
        print("🚀 بدء اختبارات الأداء الشاملة للنظام المتكامل")
        print("=" * 60)
        
        # تشغيل جميع الاختبارات
        self.test_memory_usage()
        self.test_cpu_usage()
        self.test_api_response_times()
        self.test_concurrent_users()
        self.test_database_performance()
        self.test_frontend_performance()
        self.test_ai_processing_performance()
        
        # إنشاء التقرير النهائي
        self.generate_performance_report()


if __name__ == '__main__':
    # تشغيل اختبارات الأداء
    performance_tester = SystemPerformanceTests()
    performance_tester.run_all_tests()

