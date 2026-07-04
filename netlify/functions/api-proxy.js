// Netlify serverless function — transparent proxy for TransPerth API
// Forwards requests with the required headers that the API demands.

const API_BASE = 'https://www.transperth.wa.gov.au/API/';

const HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
  'ModuleId': '5111',
  'TabId': '248',
  'X-Requested-With': 'XMLHttpRequest',
  'Referer': 'https://www.transperth.wa.gov.au/Timetables/Live-Train-Times',
  'Accept': 'application/json',
};

exports.handler = async (event) => {
  // Extract the API path — strip the Netlify function prefix
  const path = event.path.replace(/^\/\.netlify\/functions\/api-proxy\/?/, '');
  const url = API_BASE + path;

  try {
    const resp = await fetch(url, { headers: HEADERS });
    const body = await resp.text();

    return {
      statusCode: resp.status,
      headers: {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'no-cache',
      },
      body,
    };
  } catch (e) {
    return {
      statusCode: 502,
      body: JSON.stringify({ error: e.message }),
    };
  }
};
