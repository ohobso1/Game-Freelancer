#!/usr/bin/env python3
"""Frontend API Integration Tests"""
import asyncio
import httpx

async def test_frontend_integration():
    """Test that frontend can successfully call all API endpoints"""
    base_url = 'http://localhost:8000/api/v1'
    
    print("\n" + "="*60)
    print("FRONTEND API INTEGRATION TESTS")
    print("="*60 + "\n")
    
    results = []
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            # TEST 1: CORS headers
            print("✓ TEST 1: CORS headers")
            r = await client.options(f'{base_url}/freelancers')
            has_cors = 'access-control-allow-origin' in r.headers.keys()
            print(f"  CORS enabled: {'✓' if has_cors else '✗'}")
            results.append(has_cors)
            
            # TEST 2: Freelancer filtering
            print("\n✓ TEST 2: Freelancer filtering")
            r = await client.get(f'{base_url}/freelancers', params={'min_rate': 50, 'max_rate': 150})
            freelancers = r.json()['items']
            print(f"  Filtered freelancers (50-150/hr): {len(freelancers)}")
            if freelancers:
                sample = freelancers[0]
                has_normalized_fields = 'skills_normalized' in sample and 'role_tags_normalized' in sample
                print(f"  Normalized fields present: {'✓' if has_normalized_fields else '✗'}")
                results.append(has_normalized_fields)
            else:
                print("  ⚠ No freelancers in rate range")
                results.append(False)
            
            # TEST 3: Full flow - create, parse, match
            print("\n✓ TEST 3: Full flow test")
            
            # Create
            r1 = await client.post(f'{base_url}/projects', json={
                'title': 'Indie Puzzle Game',
                'raw_prompt': 'Top-down puzzle game with procedural levels. Need 1 programmer and 1 artist.'
            })
            proj = r1.json()
            proj_id = proj.get('_id') or proj.get('id')
            
            # Parse
            r2 = await client.post(f'{base_url}/parsing', json={'project_id': proj_id})
            parse_ok = r2.status_code == 200
            parsed = r2.json()['parsed_requirements'] if parse_ok else {}
            
            # Match
            r3 = await client.post(f'{base_url}/matching/{proj_id}', json={'top_n': 15})
            match_ok = r3.status_code == 200
            matches_data = r3.json() if match_ok else {}
            
            # Fetch freelancer details
            if match_ok and matches_data.get('matches'):
                freelancer_id = matches_data['matches'][0]['freelancer_id']
                r4 = await client.get(f'{base_url}/freelancers/{freelancer_id}')
                freelancer_ok = r4.status_code == 200
            else:
                freelancer_ok = False
            
            print(f"  Create project: {'✓' if r1.status_code == 200 else '✗'}")
            print(f"  Parse with Gemini: {'✓' if parse_ok else '✗'}")
            print(f"  Generate matches: {'✓' if match_ok else '✗'}")
            print(f"  Fetch freelancer: {'✓' if freelancer_ok else '✗'}")
            
            total_ok = r1.status_code == 200 and parse_ok and match_ok and freelancer_ok
            results.append(total_ok)
            
            # TEST 4: Skills normalization
            print("\n✓ TEST 4: Skills normalization")
            r = await client.get(f'{base_url}/freelancers', params={'skill': 'Unreal Engine'})
            freelancers = r.json()['items']
            has_skill = len(freelancers) > 0
            if has_skill:
                print(f"  Found {len(freelancers)} freelancers with 'Unreal Engine' skill")
                print(f"  Normalized skills in response: {'✓' if 'skills_normalized' in freelancers[0] else '✗'}")
                results.append(True)
            else:
                print("  ⚠ No freelancers with skill found")
                results.append(False)
            
            # TEST 5: Error handling
            print("\n✓ TEST 5: Error handling")
            r = await client.get(f'{base_url}/freelancers/invalid_id')
            is_404 = r.status_code == 404
            print(f"  Invalid freelancer ID returns 404: {'✓' if is_404 else '✗'}")
            results.append(is_404)
            
            print("\n" + "="*60)
            passed = sum(results)
            total = len(results)
            print(f"RESULTS: {passed}/{total} tests passed")
            if all(results):
                print("✓ FRONTEND INTEGRATION READY")
            else:
                print(f"⚠ {total - passed} test(s) failed")
            print("="*60 + "\n")
            
            return all(results)
            
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    success = asyncio.run(test_frontend_integration())
    sys.exit(0 if success else 1)
