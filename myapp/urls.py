from django.urls import path
from . import views

urlpatterns = [
    # Docs
    path('schema/', views.schema_view, name='schema'),
    path('docs/', views.swagger_ui_view, name='swagger_ui'),

    # Song
    path('songs/', views.song_list_view, name='song_list'),
    path('songs/create/', views.create_song_view, name='create_song'),
    path('songs/<uuid:song_id>/', views.song_detail_view, name='song_detail'),
    path('songs/<uuid:song_id>/update/', views.update_song_view, name='update_song'),
    path('songs/<uuid:song_id>/delete/', views.delete_song_view, name='delete_song'),

    # PlayList
    path('playlists/', views.playlist_list_view, name='playlist_list'),
    path('playlists/create/', views.create_playlist_view, name='create_playlist'),
    path('playlists/<uuid:playlist_id>/', views.playlist_detail_view, name='playlist_detail'),
    path('playlists/<uuid:playlist_id>/update/', views.update_playlist_view, name='update_playlist'),
    path('playlists/<uuid:playlist_id>/delete/', views.delete_playlist_view, name='delete_playlist'),

    # Creator
    path('creators/', views.creator_list_view, name='creator_list'),
    path('creators/create/', views.create_creator_view, name='create_creator'),
    path('creators/<uuid:creator_id>/', views.creator_detail_view, name='creator_detail'),
    path('creators/<uuid:creator_id>/update/', views.update_creator_view, name='update_creator'),
    path('creators/<uuid:creator_id>/delete/', views.delete_creator_view, name='delete_creator'),
]
