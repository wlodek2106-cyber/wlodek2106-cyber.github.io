use solana_program::pubkey::Pubkey;
use zer0life_payment_prototype::receipt_address;

fn main() {
    for (p,a,r) in [(11u8,12u8,13u8),(11,12,14),(11,14,13),(14,12,13),(51,61,71)] {
        let (address,bump)=receipt_address(&Pubkey::new_from_array([p;32]),&Pubkey::new_from_array([a;32]),&Pubkey::new_from_array([r;32]));
        println!("{p},{a},{r},{address},{bump}");
    }
}
