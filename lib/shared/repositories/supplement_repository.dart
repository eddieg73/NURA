import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:brawlerz_box/shared/models/supplement.dart';

abstract class ISupplementRepository {
  List<Supplement> getSupplements();
}

class SupplementRepository implements ISupplementRepository {
  @override
  List<Supplement> getSupplements() {
    // TODO: Connect to Commerce API (Stripe/Shopify)
    return [
      Supplement(
        id: '1',
        name: 'Whey Protein Isolate',
        description: 'Premium grass-fed whey isolate for rapid muscle recovery.',
        price: 54.99,
        imageUrl: 'https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=500',
        tags: ['Clinically Formulated', 'Third Party Tested', 'GMP Certified'],
      ),
      Supplement(
        id: '2',
        name: 'Creatine Monohydrate',
        description: 'Micro-encapsulated for superior absorption and power output.',
        price: 29.99,
        imageUrl: 'https://images.unsplash.com/photo-1549477228-8d515d39c4ef?w=500',
        tags: ['Clinically Formulated', 'GMP Certified'],
      ),
      Supplement(
        id: '3',
        name: 'Sleep Restore',
        description: 'Magnesium and Melatonin blend for deep recovery.',
        price: 34.99,
        imageUrl: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500',
        tags: ['Third Party Tested', 'GMP Certified'],
      ),
      Supplement(
        id: '4',
        name: 'Omega-3 Fish Oil',
        description: 'High potency EPA/DHA for heart and joint health.',
        price: 24.99,
        imageUrl: 'https://images.unsplash.com/photo-1576073719710-aa6e651b77bd?w=500',
        tags: ['Clinically Formulated', 'Third Party Tested'],
      ),
    ];
  }
}

final supplementRepositoryProvider = Provider<ISupplementRepository>((ref) => SupplementRepository());
