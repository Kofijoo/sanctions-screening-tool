"""Modern web dashboard for SLST"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import json

# This would be integrated with the main FastAPI app
templates = Jinja2Templates(directory="templates")

async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "SLST Dashboard",
        "active_page": "home"
    })

async def screening_interface(request: Request):
    """Interactive screening interface"""
    return templates.TemplateResponse("screening.html", {
        "request": request,
        "title": "Name Screening",
        "active_page": "screening"
    })

async def case_management(request: Request):
    """Case management interface"""
    return templates.TemplateResponse("cases.html", {
        "request": request,
        "title": "Case Management",
        "active_page": "cases"
    })

async def analytics_dashboard(request: Request):
    """Analytics and reporting dashboard"""
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "title": "Analytics",
        "active_page": "analytics"
    })

# HTML Templates (would be in separate files in production)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SLST - Sanctions Screening Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-gray-100">
    <div class="min-h-screen">
        <!-- Navigation -->
        <nav class="bg-blue-900 text-white p-4">
            <div class="container mx-auto flex justify-between items-center">
                <h1 class="text-xl font-bold">🛡️ SLST Dashboard</h1>
                <div class="space-x-4">
                    <a href="#" class="hover:text-blue-200">Screening</a>
                    <a href="#" class="hover:text-blue-200">Cases</a>
                    <a href="#" class="hover:text-blue-200">Analytics</a>
                </div>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="container mx-auto p-6">
            <!-- Quick Stats -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-sm font-medium text-gray-500">Today's Screenings</h3>
                    <p class="text-2xl font-bold text-blue-600">1,247</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-sm font-medium text-gray-500">High Risk Matches</h3>
                    <p class="text-2xl font-bold text-red-600">23</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-sm font-medium text-gray-500">Pending Review</h3>
                    <p class="text-2xl font-bold text-yellow-600">156</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-sm font-medium text-gray-500">Auto Cleared</h3>
                    <p class="text-2xl font-bold text-green-600">1,068</p>
                </div>
            </div>

            <!-- Quick Screening -->
            <div class="bg-white rounded-lg shadow p-6 mb-8">
                <h2 class="text-lg font-semibold mb-4">Quick Name Screening</h2>
                <div x-data="screeningApp()" class="space-y-4">
                    <div class="flex space-x-4">
                        <input 
                            x-model="queryName"
                            type="text" 
                            placeholder="Enter name to screen..."
                            class="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                            @keyup.enter="screenName()"
                        >
                        <button 
                            @click="screenName()"
                            :disabled="loading"
                            class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                            <span x-show="!loading">Screen</span>
                            <span x-show="loading">Screening...</span>
                        </button>
                    </div>
                    
                    <!-- Results -->
                    <div x-show="result" class="mt-6">
                        <div class="border rounded-lg p-4">
                            <div class="flex justify-between items-center mb-4">
                                <h3 class="font-semibold">Screening Results</h3>
                                <span 
                                    x-text="result?.summary?.highest_risk || 'NONE'"
                                    :class="{
                                        'bg-red-100 text-red-800': result?.summary?.highest_risk === 'HIGH',
                                        'bg-yellow-100 text-yellow-800': result?.summary?.highest_risk === 'MEDIUM',
                                        'bg-green-100 text-green-800': result?.summary?.highest_risk === 'LOW' || result?.summary?.highest_risk === 'NONE'
                                    }"
                                    class="px-3 py-1 rounded-full text-sm font-medium"
                                ></span>
                            </div>
                            
                            <div x-show="result?.matches?.length > 0">
                                <h4 class="font-medium mb-2">Matches Found:</h4>
                                <template x-for="match in result.matches">
                                    <div class="bg-gray-50 p-3 rounded mb-2">
                                        <div class="flex justify-between">
                                            <span x-text="match.target_name" class="font-medium"></span>
                                            <span x-text="match.source" class="text-sm text-gray-600"></span>
                                        </div>
                                        <div class="text-sm text-gray-600">
                                            Score: <span x-text="Math.round(match.risk_score)"></span>% | 
                                            Type: <span x-text="match.match_type"></span>
                                        </div>
                                    </div>
                                </template>
                            </div>
                            
                            <div x-show="result?.matches?.length === 0" class="text-gray-600">
                                No matches found - name appears clean
                            </div>
                            
                            <div class="mt-4 p-3 bg-blue-50 rounded">
                                <strong>Decision:</strong> <span x-text="result?.decision?.action"></span><br>
                                <strong>Reason:</strong> <span x-text="result?.decision?.reason"></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-lg font-semibold mb-4">Recent Activity</h2>
                <div class="space-y-3">
                    <div class="flex justify-between items-center p-3 bg-red-50 rounded">
                        <div>
                            <span class="font-medium">HIGH RISK:</span> Osama bin Laden
                            <span class="text-sm text-gray-600 ml-2">OFAC Match</span>
                        </div>
                        <span class="text-sm text-gray-500">2 min ago</span>
                    </div>
                    <div class="flex justify-between items-center p-3 bg-yellow-50 rounded">
                        <div>
                            <span class="font-medium">REVIEW:</span> John Smith
                            <span class="text-sm text-gray-600 ml-2">UN Match</span>
                        </div>
                        <span class="text-sm text-gray-500">5 min ago</span>
                    </div>
                    <div class="flex justify-between items-center p-3 bg-green-50 rounded">
                        <div>
                            <span class="font-medium">CLEARED:</span> Jane Doe
                            <span class="text-sm text-gray-600 ml-2">No matches</span>
                        </div>
                        <span class="text-sm text-gray-500">8 min ago</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function screeningApp() {
            return {
                queryName: '',
                result: null,
                loading: false,
                
                async screenName() {
                    if (!this.queryName.trim()) return;
                    
                    this.loading = true;
                    try {
                        const response = await fetch('/screen', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                name: this.queryName
                            })
                        });
                        
                        this.result = await response.json();
                    } catch (error) {
                        console.error('Screening failed:', error);
                        alert('Screening failed. Please try again.');
                    } finally {
                        this.loading = false;
                    }
                }
            }
        }
    </script>
</body>
</html>
"""