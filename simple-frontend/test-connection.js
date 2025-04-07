// Simple script to test connectivity to the API
const https = require('https');
const http = require('http');

// URLs to test
const urls = [
  // Base API URLs
  'http://host.docker.internal:8000',
  'http://host.docker.internal:8000/api',
  
  // Token endpoints
  'http://host.docker.internal:8000/token/',
  'http://host.docker.internal:8000/api/token/',
  
  // User endpoints
  'http://host.docker.internal:8000/users/',
  'http://host.docker.internal:8000/api/users/'
];

// Function to make a GET request to a URL
function testUrl(url) {
  return new Promise((resolve, reject) => {
    console.log(`Testing GET connection to: ${url}`);
    
    const lib = url.startsWith('https') ? https : http;
    
    const req = lib.get(url, (res) => {
      console.log(`STATUS: ${res.statusCode}`);
      console.log(`HEADERS: ${JSON.stringify(res.headers)}`);
      
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        console.log(`RESPONSE: ${data.substring(0, 200)}${data.length > 200 ? '...' : ''}`);
        resolve({ url, status: res.statusCode, success: true });
      });
    }).on('error', (e) => {
      console.error(`ERROR: ${e.message}`);
      resolve({ url, error: e.message, success: false });
    });
    
    // Set a timeout
    req.setTimeout(5000, () => {
      req.abort();
      console.error(`TIMEOUT: Connection to ${url} timed out`);
      resolve({ url, error: 'Connection timed out', success: false });
    });
  });
}

// Test login endpoint with POST request
function testLogin(url, email, password) {
  return new Promise((resolve, reject) => {
    console.log(`Testing POST login to: ${url}`);
    
    const data = JSON.stringify({
      email,
      password
    });
    
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };
    
    const lib = url.startsWith('https') ? https : http;
    
    const req = lib.request(url, options, (res) => {
      console.log(`STATUS: ${res.statusCode}`);
      console.log(`HEADERS: ${JSON.stringify(res.headers)}`);
      
      let responseData = '';
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      res.on('end', () => {
        console.log(`RESPONSE: ${responseData.substring(0, 200)}${responseData.length > 200 ? '...' : ''}`);
        resolve({ url, status: res.statusCode, success: true, data: responseData });
      });
    });
    
    req.on('error', (e) => {
      console.error(`ERROR: ${e.message}`);
      resolve({ url, error: e.message, success: false });
    });
    
    // Set a timeout
    req.setTimeout(5000, () => {
      req.abort();
      console.error(`TIMEOUT: Connection to ${url} timed out`);
      resolve({ url, error: 'Connection timed out', success: false });
    });
    
    // Write data to request body
    req.write(data);
    req.end();
  });
}

// Test all URLs
async function testAllUrls() {
  console.log('Starting API connectivity tests...');
  
  for (const url of urls) {
    await testUrl(url);
    console.log('-'.repeat(50));
  }
  
  console.log('Testing login endpoint with POST...');
  await testLogin('http://host.docker.internal:8000/token/', 'admin@example.com', 'password123');
  console.log('-'.repeat(50));
  await testLogin('http://host.docker.internal:8000/api/token/', 'admin@example.com', 'password123');
  
  console.log('API connectivity tests completed.');
}

testAllUrls().catch(console.error); 