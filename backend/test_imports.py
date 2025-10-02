try:
    from app.api.v1 import candidates
    print('candidates OK')
except Exception as e:
    print('candidates ERROR:', e)

try:
    from app.api.v1 import jobs
    print('jobs OK')
except Exception as e:
    print('jobs ERROR:', e)

try:
    from app.api.v1 import resumes
    print('resumes OK')
except Exception as e:
    print('resumes ERROR:', e)

try:
    from app.api.v1 import admin
    print('admin OK')
except Exception as e:
    print('admin ERROR:', e)

try:
    from app.api.v1 import search
    print('search OK')
except Exception as e:
    print('search ERROR:', e)

try:
    from app.api.v1 import matching
    print('matching OK')
except Exception as e:
    print('matching ERROR:', e)
