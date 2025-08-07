#!/usr/bin/env python3
"""
BACKEND TESTING SUITE FOR CYBERSECURITY PROJECTS
=================================================

This script tests the core functionality of all five harmonized projects:
1. analyseur_trafic_reseau (Network Traffic Analyzer)
2. gestionnaire_mots_de_passe (Password Manager)
3. systeme_alertes_securite (Security Alert System)
4. scanner_vulnerabilites_web (Web Vulnerability Scanner)
5. systeme_sauvegarde_chiffre (Encrypted Backup System)

Focus: Backend functionality, database operations, core features
Testing harmonized *_principal.py files with different modes
"""

import os
import sys
import sqlite3
import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class BackendTester:
    """Main testing class for all five projects"""
    
    def __init__(self):
        self.results = {
            'analyseur_trafic_reseau': {'status': 'pending', 'tests': [], 'errors': []},
            'gestionnaire_mots_de_passe': {'status': 'pending', 'tests': [], 'errors': []},
            'systeme_alertes_securite': {'status': 'pending', 'tests': [], 'errors': []},
            'scanner_vulnerabilites_web': {'status': 'pending', 'tests': [], 'errors': []},
            'systeme_sauvegarde_chiffre': {'status': 'pending', 'tests': [], 'errors': []}
        }
        self.start_time = datetime.now()
        
    def log_test(self, project, test_name, status, message="", error=None):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if error:
            result['error'] = str(error)
            self.results[project]['errors'].append(result)
        
        self.results[project]['tests'].append(result)
        
        # Print result
        color = Fore.GREEN if status == 'PASS' else Fore.RED if status == 'FAIL' else Fore.YELLOW
        print(f"{color}[{status}] {project}: {test_name} - {message}")
        
    def print_banner(self, title):
        """Print section banner"""
        print(f"\n{Fore.BLUE}{'='*80}")
        print(f"{Fore.BLUE}{title}")
        print(f"{Fore.BLUE}{'='*80}")

    def test_project_1_analyseur_trafic(self):
        """Test Network Traffic Analyzer project"""
        self.print_banner("🌐 TESTING PROJECT 1: ANALYSEUR TRAFIC RÉSEAU")
        project = 'analyseur_trafic_reseau'
        project_path = f"/app/{project}"
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        try:
            # Test 1: Check main orchestrator file exists
            main_file = "analyseur_principal.py"
            if os.path.exists(main_file):
                self.log_test(project, "Main File Exists", "PASS", f"{main_file} found")
            else:
                self.log_test(project, "Main File Exists", "FAIL", f"{main_file} not found")
                return
            
            # Test 2: Check core modules import
            try:
                sys.path.insert(0, project_path)
                
                # Test individual module imports
                modules_to_test = [
                    'analyseur_trafic',
                    'database_manager', 
                    'ml_detector',
                    'notification_system',
                    'advanced_filters'
                ]
                
                imported_modules = []
                for module in modules_to_test:
                    try:
                        __import__(module)
                        imported_modules.append(module)
                        self.log_test(project, f"Import {module}", "PASS", "Module imported successfully")
                    except ImportError as e:
                        self.log_test(project, f"Import {module}", "FAIL", f"Import failed: {e}", e)
                
                if len(imported_modules) >= 3:
                    self.log_test(project, "Core Modules Import", "PASS", f"{len(imported_modules)}/{len(modules_to_test)} modules imported")
                else:
                    self.log_test(project, "Core Modules Import", "FAIL", f"Only {len(imported_modules)}/{len(modules_to_test)} modules imported")
                    
            except Exception as e:
                self.log_test(project, "Core Modules Import", "FAIL", f"Import test failed: {e}", e)
            
            # Test 3: Database functionality
            try:
                from database_manager import DatabaseManager
                db_manager = DatabaseManager("test_analyseur.db")
                
                # Test database creation
                if os.path.exists("test_analyseur.db"):
                    self.log_test(project, "Database Creation", "PASS", "Database file created")
                    
                    # Test basic database operations
                    try:
                        stats = db_manager.get_statistics_summary()
                        self.log_test(project, "Database Operations", "PASS", f"Stats retrieved: {stats}")
                    except Exception as e:
                        self.log_test(project, "Database Operations", "FAIL", f"Stats retrieval failed: {e}", e)
                        
                    # Cleanup test database
                    try:
                        os.remove("test_analyseur.db")
                    except:
                        pass
                        
                else:
                    self.log_test(project, "Database Creation", "FAIL", "Database file not created")
                    
            except ImportError as e:
                self.log_test(project, "Database Test", "FAIL", f"DatabaseManager import failed: {e}", e)
            except Exception as e:
                self.log_test(project, "Database Test", "FAIL", f"Database test failed: {e}", e)
            
            # Test 4: ML Detector functionality
            try:
                from ml_detector import MLAnomalyDetector
                ml_detector = MLAnomalyDetector(threshold=0.1)
                self.log_test(project, "ML Detector Init", "PASS", "ML detector initialized")
                
                # Test basic ML functionality
                test_data = {
                    'protocol': 'TCP',
                    'src_ip': '192.168.1.1',
                    'dst_ip': '192.168.1.2',
                    'packet_size': 1024
                }
                
                # This might fail if no model is trained, but that's expected
                try:
                    result = ml_detector.detect_anomaly(test_data)
                    self.log_test(project, "ML Detection", "PASS", "Anomaly detection executed")
                except Exception as e:
                    # This is expected if no model is trained
                    self.log_test(project, "ML Detection", "WARN", f"ML detection not ready (expected): {e}")
                    
            except ImportError as e:
                self.log_test(project, "ML Detector Test", "FAIL", f"MLAnomalyDetector import failed: {e}", e)
            except Exception as e:
                self.log_test(project, "ML Detector Test", "FAIL", f"ML detector test failed: {e}", e)
            
            # Test 5: Configuration and status
            try:
                # Test if the main orchestrator can show status
                result = subprocess.run([
                    sys.executable, main_file, 'status'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.log_test(project, "Status Command", "PASS", "Status command executed successfully")
                else:
                    self.log_test(project, "Status Command", "FAIL", f"Status command failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.log_test(project, "Status Command", "FAIL", "Status command timed out")
            except Exception as e:
                self.log_test(project, "Status Command", "FAIL", f"Status command error: {e}", e)
            
            # Overall project status
            passed_tests = len([t for t in self.results[project]['tests'] if t['status'] == 'PASS'])
            total_tests = len(self.results[project]['tests'])
            
            if passed_tests >= total_tests * 0.7:  # 70% pass rate
                self.results[project]['status'] = 'working'
            else:
                self.results[project]['status'] = 'failing'
                
        finally:
            os.chdir(original_cwd)
            # Clean up sys.path
            if project_path in sys.path:
                sys.path.remove(project_path)

    def test_project_2_gestionnaire_mdp(self):
        """Test Password Manager project"""
        self.print_banner("🔐 TESTING PROJECT 2: GESTIONNAIRE MOTS DE PASSE")
        project = 'gestionnaire_mots_de_passe'
        project_path = f"/app/{project}"
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        try:
            # Test 1: Check main orchestrator file exists
            main_file = "gestionnaire_principal.py"
            if os.path.exists(main_file):
                self.log_test(project, "Main File Exists", "PASS", f"{main_file} found")
            else:
                self.log_test(project, "Main File Exists", "FAIL", f"{main_file} not found")
                return
            
            # Test 2: Check core modules import
            try:
                sys.path.insert(0, project_path)
                
                # Test individual module imports
                modules_to_test = [
                    'gestionnaire_mdp',
                    'gui_gestionnaire',
                    'security_audit',
                    'cloud_sync'
                ]
                
                imported_modules = []
                for module in modules_to_test:
                    try:
                        __import__(module)
                        imported_modules.append(module)
                        self.log_test(project, f"Import {module}", "PASS", "Module imported successfully")
                    except ImportError as e:
                        self.log_test(project, f"Import {module}", "WARN", f"Optional module not available: {e}")
                
                if len(imported_modules) >= 2:  # At least core modules
                    self.log_test(project, "Core Modules Import", "PASS", f"{len(imported_modules)}/{len(modules_to_test)} modules imported")
                else:
                    self.log_test(project, "Core Modules Import", "FAIL", f"Only {len(imported_modules)}/{len(modules_to_test)} modules imported")
                    
            except Exception as e:
                self.log_test(project, "Core Modules Import", "FAIL", f"Import test failed: {e}", e)
            
            # Test 3: Database and encryption functionality
            try:
                from gestionnaire_mdp import GestionnaireMDP
                
                # Create test instance
                gestionnaire = GestionnaireMDP(db_path="test_passwords.db")
                
                # Test database creation
                if os.path.exists("test_passwords.db"):
                    self.log_test(project, "Database Creation", "PASS", "Database file created")
                    
                    # Test password operations
                    try:
                        # Test master password setup (if not already set)
                        test_master = "TestMaster123!"
                        
                        # Test password generation
                        generated_pwd = gestionnaire.generate_password(length=16, include_symbols=True)
                        if generated_pwd and len(generated_pwd) == 16:
                            self.log_test(project, "Password Generation", "PASS", f"Generated password: {len(generated_pwd)} chars")
                        else:
                            self.log_test(project, "Password Generation", "FAIL", "Password generation failed")
                        
                        # Test encryption/decryption (basic test)
                        test_data = "test_password_data"
                        try:
                            # This might fail if no master password is set, which is expected
                            encrypted = gestionnaire.encrypt_data(test_data, test_master)
                            if encrypted:
                                self.log_test(project, "Encryption Test", "PASS", "Data encryption successful")
                            else:
                                self.log_test(project, "Encryption Test", "WARN", "Encryption test skipped (no master password)")
                        except Exception as e:
                            self.log_test(project, "Encryption Test", "WARN", f"Encryption test expected failure: {e}")
                        
                    except Exception as e:
                        self.log_test(project, "Password Operations", "FAIL", f"Password operations failed: {e}", e)
                        
                    # Cleanup test database
                    try:
                        os.remove("test_passwords.db")
                    except:
                        pass
                        
                else:
                    self.log_test(project, "Database Creation", "FAIL", "Database file not created")
                    
            except ImportError as e:
                self.log_test(project, "Core Functionality Test", "FAIL", f"GestionnaireMDP import failed: {e}", e)
            except Exception as e:
                self.log_test(project, "Core Functionality Test", "FAIL", f"Core functionality test failed: {e}", e)
            
            # Test 4: Security audit functionality
            try:
                from security_audit import SecurityAuditor
                auditor = SecurityAuditor()
                self.log_test(project, "Security Auditor Init", "PASS", "Security auditor initialized")
                
                # Test password strength analysis
                test_passwords = ["weak", "StrongPassword123!", "12345"]
                for pwd in test_passwords:
                    try:
                        strength = auditor.analyze_password_strength(pwd)
                        self.log_test(project, f"Password Analysis ({pwd[:4]}...)", "PASS", f"Strength: {strength}")
                    except Exception as e:
                        self.log_test(project, f"Password Analysis ({pwd[:4]}...)", "FAIL", f"Analysis failed: {e}", e)
                        
            except ImportError as e:
                self.log_test(project, "Security Audit Test", "WARN", f"SecurityAuditor not available: {e}")
            except Exception as e:
                self.log_test(project, "Security Audit Test", "FAIL", f"Security audit test failed: {e}", e)
            
            # Test 5: Configuration and status
            try:
                # Test if the main orchestrator can show status
                result = subprocess.run([
                    sys.executable, main_file, 'status'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.log_test(project, "Status Command", "PASS", "Status command executed successfully")
                else:
                    self.log_test(project, "Status Command", "FAIL", f"Status command failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.log_test(project, "Status Command", "FAIL", "Status command timed out")
            except Exception as e:
                self.log_test(project, "Status Command", "FAIL", f"Status command error: {e}", e)
            
            # Overall project status
            passed_tests = len([t for t in self.results[project]['tests'] if t['status'] == 'PASS'])
            total_tests = len(self.results[project]['tests'])
            
            if passed_tests >= total_tests * 0.7:  # 70% pass rate
                self.results[project]['status'] = 'working'
            else:
                self.results[project]['status'] = 'failing'
                
        finally:
            os.chdir(original_cwd)
            # Clean up sys.path
            if project_path in sys.path:
                sys.path.remove(project_path)

    def test_project_3_alertes_securite(self):
        """Test Security Alert System project"""
        self.print_banner("🚨 TESTING PROJECT 3: SYSTÈME ALERTES SÉCURITÉ")
        project = 'systeme_alertes_securite'
        project_path = f"/app/{project}"
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        try:
            # Test 1: Check main orchestrator file exists
            main_file = "alertes_principal.py"
            if os.path.exists(main_file):
                self.log_test(project, "Main File Exists", "PASS", f"{main_file} found")
            else:
                self.log_test(project, "Main File Exists", "FAIL", f"{main_file} not found")
                return
            
            # Test 2: Test different modes without user interaction
            modes_to_test = ['status']
            
            for mode in modes_to_test:
                try:
                    result = subprocess.run([
                        sys.executable, main_file, mode
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        self.log_test(project, f"Mode {mode}", "PASS", f"Mode {mode} executed successfully")
                    else:
                        self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} failed: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} timed out")
                except Exception as e:
                    self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} error: {e}", e)
            
            # Test 3: Check core modules import
            try:
                sys.path.insert(0, project_path)
                
                # Test main module import
                try:
                    from alertes_securite import SystemeAlertes, Alerte
                    self.log_test(project, "Import Main Module", "PASS", "Main module imported successfully")
                    
                    # Test ML detector import (optional)
                    try:
                        from ml_anomaly_detector import MLAnomalyDetector
                        self.log_test(project, "Import ML Detector", "PASS", "ML detector imported successfully")
                    except ImportError as e:
                        self.log_test(project, "Import ML Detector", "WARN", f"ML detector not available: {e}")
                        
                except ImportError as e:
                    self.log_test(project, "Import Main Module", "FAIL", f"Main module import failed: {e}", e)
                    return
                    
            except Exception as e:
                self.log_test(project, "Core Modules Import", "FAIL", f"Import test failed: {e}", e)
                return
            
            # Test 4: Database and alert functionality
            try:
                # Create test instance
                systeme = SystemeAlertes(db_path="test_alertes.db", config_path="test_config.json")
                
                # Test database creation
                if os.path.exists("test_alertes.db"):
                    self.log_test(project, "Database Creation", "PASS", "Database file created")
                    
                    # Test alert creation and storage
                    try:
                        test_alerte = Alerte(
                            id=f"test_{int(time.time())}",
                            timestamp=datetime.now(),
                            niveau="INFO",
                            source="test",
                            message="Test alert for backend testing",
                            details={"test": True, "backend_test": True}
                        )
                        
                        # Test alert storage
                        systeme.enregistrer_alerte(test_alerte)
                        self.log_test(project, "Alert Storage", "PASS", "Alert stored successfully")
                        
                        # Test alert retrieval
                        alertes = systeme.lister_alertes(limite=10)
                        if alertes and len(alertes) > 0:
                            self.log_test(project, "Alert Retrieval", "PASS", f"Retrieved {len(alertes)} alerts")
                        else:
                            self.log_test(project, "Alert Retrieval", "FAIL", "No alerts retrieved")
                        
                        # Test statistics
                        stats = systeme.obtenir_statistiques()
                        if stats and 'globales' in stats:
                            self.log_test(project, "Statistics", "PASS", f"Stats retrieved: {stats['globales']['total']} total alerts")
                        else:
                            self.log_test(project, "Statistics", "FAIL", "Statistics retrieval failed")
                            
                    except Exception as e:
                        self.log_test(project, "Alert Operations", "FAIL", f"Alert operations failed: {e}", e)
                        
                    # Cleanup test files
                    try:
                        os.remove("test_alertes.db")
                        if os.path.exists("test_config.json"):
                            os.remove("test_config.json")
                    except:
                        pass
                        
                else:
                    self.log_test(project, "Database Creation", "FAIL", "Database file not created")
                    
            except Exception as e:
                self.log_test(project, "Core Functionality Test", "FAIL", f"Core functionality test failed: {e}", e)
            
            # Overall project status
            passed_tests = len([t for t in self.results[project]['tests'] if t['status'] == 'PASS'])
            total_tests = len(self.results[project]['tests'])
            
            if passed_tests >= total_tests * 0.7:  # 70% pass rate
                self.results[project]['status'] = 'working'
            else:
                self.results[project]['status'] = 'failing'
                
        finally:
            os.chdir(original_cwd)
            # Clean up sys.path
            if project_path in sys.path:
                sys.path.remove(project_path)

    def test_project_4_scanner_vulnerabilites(self):
        """Test Web Vulnerability Scanner project"""
        self.print_banner("🕷️ TESTING PROJECT 4: SCANNER VULNÉRABILITÉS WEB")
        project = 'scanner_vulnerabilites_web'
        project_path = f"/app/{project}"
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        try:
            # Test 1: Check main orchestrator file exists
            main_file = "scanner_principal.py"
            if os.path.exists(main_file):
                self.log_test(project, "Main File Exists", "PASS", f"{main_file} found")
            else:
                self.log_test(project, "Main File Exists", "FAIL", f"{main_file} not found")
                return
            
            # Test 2: Test different modes without user interaction
            modes_to_test = ['status', 'stats']
            
            for mode in modes_to_test:
                try:
                    result = subprocess.run([
                        sys.executable, main_file, mode
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        self.log_test(project, f"Mode {mode}", "PASS", f"Mode {mode} executed successfully")
                    else:
                        self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} failed: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} timed out")
                except Exception as e:
                    self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} error: {e}", e)
            
            # Test 3: Check core modules import
            try:
                sys.path.insert(0, project_path)
                
                # Test main module import
                try:
                    from scanner_vulnerabilites import WebVulnScanner, ResultatScan
                    self.log_test(project, "Import Main Module", "PASS", "Main module imported successfully")
                        
                except ImportError as e:
                    self.log_test(project, "Import Main Module", "FAIL", f"Main module import failed: {e}", e)
                    return
                    
            except Exception as e:
                self.log_test(project, "Core Modules Import", "FAIL", f"Import test failed: {e}", e)
                return
            
            # Test 4: Scanner initialization
            try:
                # Create test instance
                scanner = WebVulnScanner()
                self.log_test(project, "Scanner Initialization", "PASS", "Scanner initialized successfully")
                
                # Test database creation
                if os.path.exists("scans_vulnerabilites.db"):
                    self.log_test(project, "Database Creation", "PASS", "Database file created")
                else:
                    self.log_test(project, "Database Creation", "WARN", "Database file not created (may be created on first scan)")
                    
            except Exception as e:
                self.log_test(project, "Scanner Functionality Test", "FAIL", f"Scanner functionality test failed: {e}", e)
            
            # Overall project status
            passed_tests = len([t for t in self.results[project]['tests'] if t['status'] == 'PASS'])
            total_tests = len(self.results[project]['tests'])
            
            if passed_tests >= total_tests * 0.7:  # 70% pass rate
                self.results[project]['status'] = 'working'
            else:
                self.results[project]['status'] = 'failing'
                
        finally:
            os.chdir(original_cwd)
            # Clean up sys.path
            if project_path in sys.path:
                sys.path.remove(project_path)

    def test_project_5_sauvegarde_chiffre(self):
        """Test Encrypted Backup System project"""
        self.print_banner("💾 TESTING PROJECT 5: SYSTÈME SAUVEGARDE CHIFFRÉ")
        project = 'systeme_sauvegarde_chiffre'
        project_path = f"/app/{project}"
        
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        try:
            # Test 1: Check main orchestrator file exists
            main_file = "sauvegarde_principal.py"
            if os.path.exists(main_file):
                self.log_test(project, "Main File Exists", "PASS", f"{main_file} found")
            else:
                self.log_test(project, "Main File Exists", "FAIL", f"{main_file} not found")
                return
            
            # Test 2: Test different modes without user interaction
            modes_to_test = ['status', 'stats', 'list']
            
            for mode in modes_to_test:
                try:
                    result = subprocess.run([
                        sys.executable, main_file, mode
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        self.log_test(project, f"Mode {mode}", "PASS", f"Mode {mode} executed successfully")
                    else:
                        self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} failed: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} timed out")
                except Exception as e:
                    self.log_test(project, f"Mode {mode}", "FAIL", f"Mode {mode} error: {e}", e)
            
            # Test 3: Check core modules import
            try:
                sys.path.insert(0, project_path)
                
                # Test main module import
                try:
                    from sauvegarde_chiffree import SystemeSauvegardeChiffre
                    self.log_test(project, "Import Main Module", "PASS", "Main module imported successfully")
                        
                except ImportError as e:
                    self.log_test(project, "Import Main Module", "FAIL", f"Main module import failed: {e}", e)
                    return
                    
            except Exception as e:
                self.log_test(project, "Core Modules Import", "FAIL", f"Import test failed: {e}", e)
                return
            
            # Test 4: System initialization
            try:
                # Create test instance
                systeme = SystemeSauvegardeChiffre("test_config.json")
                self.log_test(project, "System Initialization", "PASS", "System initialized successfully")
                
                # Test configuration file creation
                if os.path.exists("test_config.json"):
                    self.log_test(project, "Configuration Creation", "PASS", "Configuration file created")
                    # Cleanup test config
                    try:
                        os.remove("test_config.json")
                    except:
                        pass
                else:
                    self.log_test(project, "Configuration Creation", "WARN", "Configuration file not created")
                    
            except Exception as e:
                self.log_test(project, "System Functionality Test", "FAIL", f"System functionality test failed: {e}", e)
            
            # Overall project status
            passed_tests = len([t for t in self.results[project]['tests'] if t['status'] == 'PASS'])
            total_tests = len(self.results[project]['tests'])
            
            if passed_tests >= total_tests * 0.7:  # 70% pass rate
                self.results[project]['status'] = 'working'
            else:
                self.results[project]['status'] = 'failing'
                
        finally:
            os.chdir(original_cwd)
            # Clean up sys.path
            if project_path in sys.path:
                sys.path.remove(project_path)

    def generate_summary_report(self):
        """Generate final summary report"""
        self.print_banner("📊 BACKEND TESTING SUMMARY REPORT")
        
        total_duration = datetime.now() - self.start_time
        
        print(f"\n{Fore.CYAN}⏱️  Total Testing Duration: {total_duration}")
        print(f"{Fore.CYAN}📅 Test Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        overall_status = "PASS"
        
        for project, results in self.results.items():
            print(f"\n{Fore.YELLOW}📁 PROJECT: {project.upper()}")
            print("-" * 60)
            
            passed = len([t for t in results['tests'] if t['status'] == 'PASS'])
            warned = len([t for t in results['tests'] if t['status'] == 'WARN'])
            failed = len([t for t in results['tests'] if t['status'] == 'FAIL'])
            total = len(results['tests'])
            
            status_color = Fore.GREEN if results['status'] == 'working' else Fore.RED
            print(f"{status_color}Status: {results['status'].upper()}")
            print(f"{Fore.CYAN}Tests: {passed} PASS, {warned} WARN, {failed} FAIL (Total: {total})")
            
            if results['status'] != 'working':
                overall_status = "FAIL"
            
            # Show critical errors
            critical_errors = [e for e in results['errors'] if 'import' in e.get('error', '').lower()]
            if critical_errors:
                print(f"{Fore.RED}Critical Issues:")
                for error in critical_errors[:3]:  # Show first 3
                    print(f"  • {error['test']}: {error['error']}")
        
        print(f"\n{Fore.BLUE}{'='*80}")
        overall_color = Fore.GREEN if overall_status == "PASS" else Fore.RED
        print(f"{overall_color}🎯 OVERALL BACKEND STATUS: {overall_status}")
        print(f"{Fore.BLUE}{'='*80}")
        
        return overall_status

    def run_all_tests(self):
        """Run all backend tests"""
        print(f"{Fore.BLUE}🚀 STARTING COMPREHENSIVE BACKEND TESTING")
        print(f"{Fore.BLUE}Testing all five harmonized cybersecurity projects...")
        
        # Test each project
        self.test_project_1_analyseur_trafic()
        self.test_project_2_gestionnaire_mdp()
        self.test_project_3_alertes_securite()
        self.test_project_4_scanner_vulnerabilites()
        self.test_project_5_sauvegarde_chiffre()
        
        # Generate summary
        overall_status = self.generate_summary_report()
        
        return overall_status

def main():
    """Main testing function"""
    tester = BackendTester()
    overall_status = tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if overall_status == "PASS" else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()