#!/usr/bin/env python3
"""E2E Verification Tests for Game-Freelancer MVP"""
import asyncio
import httpx
import sys

async def run_tests():
    """Run comprehensive API tests"""
    base_url = 'http://localhost:8000/api/v1'
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            print("\n" + "="*60)
            print("GAME-FREELANCER E2E VERIFICATION TESTS")
            print("="*60 + "\n")
            
            # TEST 1: Get freelancers count
            print("✓ TEST 1: List freelancers")
            try:
                r = await client.get(f'{base_url}/freelancers')
                resp = r.json()
                freelancers = resp['items'] if 'items' in resp else resp
                print(f"  Status: {r.status_code}")
                print(f"  Freelancers in database: {len(freelancers)}")
                if len(freelancers) == 0:
                    print("  ⚠ WARNING: No freelancers found. Database may not be seeded.")
                    return False
                print(f"  Sample: {freelancers[0]['display_name']}")
            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                return False
            
            # TEST 2: Create project
            print("\n✓ TEST 2: Create project")
            try:
                r = await client.post(f'{base_url}/projects', json={
                    'title': 'Space Adventure',
                    'raw_prompt': 'Multiplayer 3D sci-fi game with procedural planets. Need gameplay programmers, graphics engineers, and pixel artists.'
                })
                if r.status_code != 200:
                    print(f"  ✗ FAILED: Status {r.status_code}")
                    return False
                
                project = r.json()
                proj_id = project.get('id') or project.get('_id')
                print(f"  Status: {r.status_code}")
                print(f"  Project ID: {proj_id}")
                print(f"  Title: {project['title']}")
            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # TEST 3: Parse project with Gemini
            print("\n✓ TEST 3: Parse project with Gemini")
            try:
                r = await client.post(f'{base_url}/parsing', json={'project_id': proj_id})
                if r.status_code != 200:
                    print(f"  ✗ FAILED: Status {r.status_code}, Response: {r.text[:200]}")
                    return False
                
                resp_obj = r.json()
                parsed = resp_obj['parsed_requirements']
                print(f"  Status: {r.status_code}")
                print(f"  Parsed roles: {len(parsed['roles'])}")
                if parsed['roles']:
                    for role in parsed['roles'][:2]:
                        print(f"    - {role['role_name']} ({role['count']}x {role['seniority']})")
                
                print(f"  Required skills: {len(parsed['required_skills'])}")
                if parsed['required_skills']:
                    print(f"    {', '.join(parsed['required_skills'][:3])}...")
                
                print(f"  Optional skills: {len(parsed.get('optional_skills', []))}")
            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # TEST 4: Generate matches
            print("\n✓ TEST 4: Generate matches")
            try:
                r = await client.post(f'{base_url}/matching/{proj_id}', json={'top_n': 20})
                if r.status_code != 200:
                    print(f"  ✗ FAILED: Status {r.status_code}, Response: {r.text}")
                    return False
                
                matches_resp = r.json()
                matches = matches_resp['matches']
                print(f"  Status: {r.status_code}")
                print(f"  Matches found: {len(matches)}")
                
                if matches:
                    top_match = matches[0]
                    print(f"  Top match score: {top_match['score']:.2f} (rank {top_match['rank']})")
                    print(f"  Matched skills: {', '.join(top_match['matched_required_skills'][:2])}")
            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                return False
            
            # TEST 5: Get freelancer details for top match
            print("\n✓ TEST 5: Get freelancer details")
            try:
                if not matches:
                    print("  ⚠ No matches to verify")
                else:
                    freelancer_id = matches[0]['freelancer_id']
                    r = await client.get(f'{base_url}/freelancers/{freelancer_id}')
                    if r.status_code != 200:
                        print(f"  ✗ FAILED: Status {r.status_code}")
                        return False
                    
                    freelancer = r.json()
                    print(f"  Status: {r.status_code}")
                    print(f"  Name: {freelancer.get('display_name', 'N/A')}")
                    print(f"  Experience: {freelancer.get('years_experience', 'N/A')} years")
                    skills = freelancer.get('skills_normalized', [])
                    print(f"  Skills: {len(skills)} (normalized)")
                    if skills:
                        print(f"    {', '.join(skills[:3])}...")
                    roles = freelancer.get('role_tags_normalized', [])
                    print(f"  Roles: {', '.join(roles[:2]) if roles else 'N/A'}")
                    print(f"  Rate: ${freelancer.get('hourly_rate', 'N/A')}/hr")
            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            # TEST 6: Verify parsed requirements are consumed
            print("\n✓ TEST 6: Verify parsed requirements stored")
            try:
                r = await client.get(f'{base_url}/projects/{proj_id}')
                if r.status_code != 200:
                    print(f"  ✗ FAILED: Status {r.status_code}")
                    return False
                
                stored_project = r.json()
                print(f"  Status: {r.status_code}")
                print(f"  Project status: {stored_project['status']}")
                print(f"  Project persisted: ✓")
            except Exception as e:
                print(f"  ✗ FAILED: {e}")
                return False
            
            print("\n" + "="*60)
            print("✓ ALL TESTS PASSED")
            print("="*60 + "\n")
            return True
            
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        return False

if __name__ == '__main__':
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
