class User {
  final int id;
  final String username;
  final String? firstName;
  final String? lastName;
  final String? email;
  final String? phoneNumber;
  final String? avatar;
  final String? avatarUrl;
  final bool hasSubscription;
  final String subscriptionType;
  final DateTime? subscriptionStartDate;
  final DateTime? subscriptionEndDate;
  final bool subscriptionAutoRenew;
  final int level;
  final Map<String, dynamic> experience;
  final DateTime? dateJoined;

  User({
    required this.id,
    required this.username,
    this.firstName,
    this.lastName,
    this.email,
    this.phoneNumber,
    this.avatar,
    this.avatarUrl,
    this.hasSubscription = false,
    this.subscriptionType = 'free',
    this.subscriptionStartDate,
    this.subscriptionEndDate,
    this.subscriptionAutoRenew = false,
    this.level = 1,
    this.experience = const {},
    this.dateJoined,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    // Формируем полный URL для аватарки
    String? avatarUrl;
    if (json['avatar'] != null && json['avatar'].toString().isNotEmpty) {
      final avatar = json['avatar'].toString();
      if (avatar.startsWith('http')) {
        avatarUrl = avatar;
      } else {
        // Добавляем базовый URL сервера
        avatarUrl = 'http://147.45.214.86:8080$avatar';
      }
    }
    
    return User(
      id: json['id'],
      username: json['username'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      email: json['email'],
      phoneNumber: json['phone_number'],
      avatar: json['avatar'],
      avatarUrl: avatarUrl,
      hasSubscription: json['has_subscription'] ?? false,
      subscriptionType: json['subscription_type'] ?? 'free',
      subscriptionStartDate: json['subscription_start_date'] != null 
          ? DateTime.parse(json['subscription_start_date'])
          : null,
      subscriptionEndDate: json['subscription_end_date'] != null 
          ? DateTime.parse(json['subscription_end_date'])
          : null,
      subscriptionAutoRenew: json['subscription_auto_renew'] ?? false,
      level: (json['level'] as num?)?.toInt() ?? 1,
      experience: json['experience'] is Map<String, dynamic>
          ? Map<String, dynamic>.from(json['experience'] as Map<String, dynamic>)
          : <String, dynamic>{},
      dateJoined: json['date_joined'] != null ? DateTime.parse(json['date_joined']) : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'phone_number': phoneNumber,
      'avatar': avatar,
      'avatar_url': avatarUrl,
      'has_subscription': hasSubscription,
      'subscription_type': subscriptionType,
      'subscription_start_date': subscriptionStartDate?.toIso8601String(),
      'subscription_end_date': subscriptionEndDate?.toIso8601String(),
      'subscription_auto_renew': subscriptionAutoRenew,
      'level': level,
      'experience': experience,
      'date_joined': dateJoined?.toIso8601String(),
    };
  }

  String get displayName {
    if (firstName != null && lastName != null) {
      return '$firstName $lastName';
    } else if (firstName != null) {
      return firstName!;
    } else if (lastName != null) {
      return lastName!;
    } else {
      return username;
    }
  }

  int get daysSinceJoin {
    final dj = dateJoined;
    if (dj == null) return 0;
    final now = DateTime.now();
    final start = DateTime(dj.year, dj.month, dj.day);
    final today = DateTime(now.year, now.month, now.day);
    return today.difference(start).inDays + 1; // включительно: первый день = 1
  }

  String get subscriptionDisplayName {
    switch (subscriptionType) {
      case 'free':
        return 'Базовая'; // Будет заменено на локализацию в UI
      case 'premium':
        return 'Премиум'; // Будет заменено на локализацию в UI
      case 'pro':
        return 'Премиум'; // Будет заменено на локализацию в UI
      default:
        return 'Базовая'; // Будет заменено на локализацию в UI
    }
  }

  bool get isSubscriptionActive {
    if (!hasSubscription) return false;
    if (subscriptionEndDate == null) return true;
    return DateTime.now().isBefore(subscriptionEndDate!);
  }
}
