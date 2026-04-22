from django.urls import path
from . import views

urlpatterns = [
    # Enums
    path('enums/', views.enum_choices_view, name='enum_choices'),

    # Mock audio (dev only)
    path('mock-audio/<str:filename>', views.mock_audio_view, name='mock_audio'),

    # Song
    path('songs/', views.song_list_view, name='song_list'),
    path('songs/generate/', views.generate_song_view, name='generate_song'),
    path('songs/callback/', views.suno_callback_view, name='suno_callback'),
    path('songs/create/', views.create_song_view, name='create_song'),
    path('songs/<uuid:song_id>/', views.song_detail_view, name='song_detail'),
    path('songs/<uuid:song_id>/update/', views.update_song_view, name='update_song'),
    path('songs/<uuid:song_id>/delete/', views.delete_song_view, name='delete_song'),
    path('songs/<uuid:song_id>/regenerate/', views.regenerate_song_view, name='regenerate_song'),

    # PlayList
    path('playlists/', views.playlist_list_view, name='playlist_list'),
    path('playlists/create/', views.create_playlist_view, name='create_playlist'),
    path('playlists/<uuid:playlist_id>/', views.playlist_detail_view, name='playlist_detail'),
    path('playlists/<uuid:playlist_id>/update/', views.update_playlist_view, name='update_playlist'),
    path('playlists/<uuid:playlist_id>/delete/', views.delete_playlist_view, name='delete_playlist'),

    # Creator
    path('creators/', views.creator_list_view, name='creator_list'),
    path('creators/sync/', views.sync_creator_view, name='sync_creator'),
    path('creators/create/', views.create_creator_view, name='create_creator'),
    path('creators/<uuid:creator_id>/', views.creator_detail_view, name='creator_detail'),
    path('creators/<uuid:creator_id>/update/', views.update_creator_view, name='update_creator'),
    path('creators/<uuid:creator_id>/delete/', views.delete_creator_view, name='delete_creator'),
]
