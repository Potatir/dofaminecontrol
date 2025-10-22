import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import 'api_client.dart';

class AuthService {
  AuthService(this._api);
  final ApiClient _api;

  static const _kAccess = 'access_token';
  static const _kRefresh = 'refresh_token';

  Future<void> saveTokens(String access, String refresh) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_kAccess, access);
    await prefs.setString(_kRefresh, refresh);
  }

  Future<String?> get accessToken async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_kAccess);
  }

  Future<String?> get refreshToken async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_kRefresh);
  }

  Future<bool> refreshAccessToken() async {
    final rt = await refreshToken;
    if (rt == null || rt.isEmpty) return false;
    try {
      final resp = await _api.postJson('/auth/token/refresh/', body: {
        'refresh': rt,
      });
      final newAccess = resp['access'] as String?;
      if (newAccess != null && newAccess.isNotEmpty) {
        // сохраняем новый access, оставляем текущий refresh
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString(_kAccess, newAccess);
        return true;
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  /// Возвращает валидный access token, обновляя если он истекает/истёк
  Future<String?> ensureAccessToken() async {
    final token = await accessToken;
    if (token != null && token.isNotEmpty) {
      final expiresAt = _decodeJwtExpiry(token);
      final nowSec = DateTime.now().millisecondsSinceEpoch ~/ 1000;
      // Обновляем заранее, если осталось < 60 секунд
      if (expiresAt != null && expiresAt - nowSec > 60) {
        return token;
      }
    }
    final ok = await refreshAccessToken();
    if (!ok) return null;
    return await accessToken;
  }

  int? _decodeJwtExpiry(String jwt) {
    try {
      final parts = jwt.split('.');
      if (parts.length != 3) return null;
      final payload = parts[1]
          .replaceAll('-', '+')
          .replaceAll('_', '/');
      var normalized = payload;
      while (normalized.length % 4 != 0) {
        normalized += '=';
      }
      final decoded = base64Decode(normalized);
      final map = jsonDecode(String.fromCharCodes(decoded)) as Map<String, dynamic>;
      final exp = map['exp'];
      if (exp is int) return exp;
      if (exp is String) return int.tryParse(exp);
      return null;
    } catch (_) {
      return null;
    }
  }

  /// Проверяет валидность токена на сервере
  Future<bool> isTokenValid() async {
    try {
      final token = await ensureAccessToken();
      if (token == null) return false;
      
      // Делаем запрос к защищенному эндпоинту для проверки токена
      await _api.getJson('/users/me/', bearerToken: token);
      return true;
    } catch (e) {
      print('Token validation failed: $e');
      return false;
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    // НЕ удаляем токены - оставляем пользователя залогиненным
    // await prefs.remove(_kAccess);
    // await prefs.remove(_kRefresh);
  }

  Future<void> register({
    required String username,
    required String password,
    String? email,
    String? firstName,
    String? lastName,
    String? phoneNumber,
  }) async {
    await _api.postJson('/auth/register/', body: {
      'username': username,
      'password': password,
      if (email != null) 'email': email,
      if (firstName != null) 'first_name': firstName,
      if (lastName != null) 'last_name': lastName,
      if (phoneNumber != null) 'phone_number': phoneNumber,
    });
  }

  Future<void> loginWithPassword({required String identifier, required String password}) async {
    final resp = await _api.postJson('/auth/token/', body: {
      'username': identifier,
      'password': password,
    });
    await saveTokens(resp['access'] as String, resp['refresh'] as String);
  }

  Future<void> loginWithSms({required String phoneNumber, required String code}) async {
    final resp = await _api.postJson('/auth/sms/verify/', body: {
      'phone_number': phoneNumber,
      'code': code,
    });
    await saveTokens(resp['access'] as String, resp['refresh'] as String);
  }

  Future<void> socialLoginStub({required String provider, required String externalId, String? email}) async {
    final resp = await _api.postJson('/auth/social/$provider/', body: {
      'external_id': externalId,
      if (email != null) 'email': email,
    });
    await saveTokens(resp['access'] as String, resp['refresh'] as String);
  }

}


